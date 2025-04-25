from sqlalchemy.orm import Session
from typing import Dict, Any
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