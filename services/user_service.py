from sqlalchemy.orm import Session
from typing import Dict, Any
from models import User, LicensePlate

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