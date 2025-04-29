from sqlalchemy.orm import Session
import hashlib
from typing import Optional
from models import User
from fastapi import HTTPException, Depends, Request
from routes.schemas import UserLogin, UserSignup
from database import get_db
from services.session_service import SessionService
from services.email_service import EmailService

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    """Generate a hash for the given password."""
    return hashlib.sha256(password.encode()).hexdigest()

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    session_service = SessionService(request)
    user_id = session_service.get_user_id()
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    auth_service = AuthService(db)
    user = auth_service.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_idnumber(self, idnumber: str) -> Optional[User]:
        return self.db.query(User).filter(User.idnumber == idnumber).first()

    async def login_user(self, username: str, password: str) -> User:
        # Validate input using schema
        login_data = UserLogin(username=username, password=password)
        
        # Verify user
        user = self.verify_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        
        # Check if user is banned
        if user.is_banned:
            raise HTTPException(status_code=400, detail="Your account has been banned")
        
        return user

    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        confirm_password: str,
        firstname: str,
        lastname: str,
        idnumber: str,
        address: str,
        phone_number: str,
        iban: Optional[str] = None
    ) -> User:
        print(f"Debug - Attempting to register with email: {email}")  # Debug log
        try:
            # Validate input using schema
            signup_data = UserSignup(
                username=username,
                email=email,
                password=password,
                confirm_password=confirm_password,
                firstname=firstname,
                lastname=lastname,
                idnumber=idnumber,
                address=address,
                phone_number=phone_number,
                iban=iban
            )
        except Exception as e:
            print(f"Debug - Validation error: {str(e)}")  # Debug log
            raise HTTPException(status_code=400, detail=str(e))
        
        # Validate passwords match
        if signup_data.password != signup_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        # Check if username exists
        if self.get_user_by_username(signup_data.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check if email exists
        if self.get_user_by_email(signup_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if ID number exists and if user is banned
        existing_user = self.get_user_by_idnumber(signup_data.idnumber)
        if existing_user:
            if existing_user.is_banned:
                raise HTTPException(status_code=400, detail="This ID number is banned from registration")
            else:
                raise HTTPException(status_code=400, detail="ID number already registered")
        
        # Create user
        user = self.create_user(
            username=signup_data.username,
            email=signup_data.email,
            password=signup_data.password,
            firstname=signup_data.firstname,
            lastname=signup_data.lastname,
            idnumber=signup_data.idnumber,
            address=signup_data.address,
            phone_number=signup_data.phone_number,
            iban=signup_data.iban
        )

        # Send welcome email
        email_service = EmailService()
        email_service.send_welcome_email(user.email, user.username)
        
        return user

    def create_user(self, username: str, email: str, password: str, firstname: str, lastname: str, idnumber: str, address: str, phone_number: Optional[str] = None, iban: Optional[str] = None) -> User:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        db_user = User(
            username=username,
            email=email,
            password=hashed_password,
            firstname=firstname,
            lastname=lastname,
            idnumber=idnumber,
            address=address,
            phone_number=phone_number,
            iban=iban
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def verify_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user.password == hashed_password:
            return user
        return None 