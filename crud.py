from sqlalchemy.orm import Session
from models import User, Listing
import hashlib
from typing import Optional

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    db_user = User(username=username, email=email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user.password == hashed_password:
        return user
    return None

def create_listing(db: Session, plate_number: str, description: str, 
                  price: float, listing_type: str, owner_id: int, 
                  image_path: Optional[str] = None):
    db_listing = Listing(
        plate_number=plate_number,
        description=description,
        price=price,
        listing_type=listing_type,
        owner_id=owner_id,
        image_path=image_path
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Listing).offset(skip).limit(limit).all()

def get_listing(db: Session, listing_id: int):
    return db.query(Listing).filter(Listing.id == listing_id).first()

def get_user_listings(db: Session, user_id: int):
    return db.query(Listing).filter(Listing.owner_id == user_id).all()

def get_listings_by_type(db: Session, listing_type: str):
    return db.query(Listing).filter(Listing.listing_type == listing_type).all() 