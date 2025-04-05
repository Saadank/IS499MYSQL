from sqlalchemy.orm import Session
import hashlib
from typing import Optional
from models import User
from fastapi import HTTPException, Depends
from routes.schemas import UserLogin, UserSignup
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import get_db

security = HTTPBasic()

async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    auth_service = AuthService(db)
    user = auth_service.verify_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
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

    async def login_user(self, username: str, password: str) -> User:
        # Validate input using schema
        login_data = UserLogin(username=username, password=password)
        
        # Verify user
        user = self.verify_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        
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
        address: str
    ) -> User:
        # Validate input using schema
        signup_data = UserSignup(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            firstname=firstname,
            lastname=lastname,
            idnumber=idnumber,
            address=address
        )
        
        # Validate passwords match
        if signup_data.password != signup_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        # Check if username exists
        if self.get_user_by_username(signup_data.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check if email exists
        if self.get_user_by_email(signup_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        return self.create_user(
            username=signup_data.username,
            email=signup_data.email,
            password=signup_data.password,
            firstname=signup_data.firstname,
            lastname=signup_data.lastname,
            idnumber=signup_data.idnumber,
            address=signup_data.address
        )

    def create_user(self, username: str, email: str, password: str, firstname: str, lastname: str, idnumber: str, address: str) -> User:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        db_user = User(
            username=username,
            email=email,
            password=hashed_password,
            firstname=firstname,
            lastname=lastname,
            idnumber=idnumber,
            address=address
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