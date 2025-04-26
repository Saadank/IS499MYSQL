from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from models import User, LicensePlate, WishlistItem, Order
from schemas import UserCreate, UserUpdate
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_profile_data(self, user_id: int) -> Dict[str, Any]:
        user = self.db.query(User).filter(User.id == user_id).first()
        listings = self.db.query(LicensePlate).filter(LicensePlate.owner_id == user_id).all()
        
        return {
            "user": user,
            "listings": listings
        }

    def get_user(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_listings(self, user_id: int) -> list[LicensePlate]:
        return self.db.query(LicensePlate).filter(LicensePlate.owner_id == user_id).all()

    def get_user_orders(self, user_id: int):
        """
        Retrieve all orders (both purchases and sales) for a specific user.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get both purchases and sales
        purchases = (
            self.db.query(Order)
            .filter(Order.buyer_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

        sales = (
            self.db.query(Order)
            .filter(Order.seller_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

        return {
            "purchases": purchases,
            "sales": sales
        }

    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone_number == phone_number).first()

    def update_user_phone(self, user_id: int, phone_number: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate phone number format
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits")
        
        # Check if phone number is already taken by another user
        existing_user = self.get_user_by_phone(phone_number)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="Phone number already registered")
        
        user.phone_number = phone_number
        self.db.commit()

    def update_user_iban(self, user_id: int, iban: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.iban = iban
        self.db.commit()

    def update_user_password(self, user_id: int, hashed_password: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.password = hashed_password
        self.db.commit() 