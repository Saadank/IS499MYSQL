from sqlalchemy.orm import Session
from typing import List, Optional
from models import WishlistItem, LicensePlate

class WishlistService:
    def __init__(self, db: Session):
        self.db = db

    def add_to_wishlist(self, user_id: int, plate_id: int) -> Optional[WishlistItem]:
        """Add a license plate to user's wishlist"""
        try:
            wishlist_item = WishlistItem(user_id=user_id, plate_id=plate_id)
            self.db.add(wishlist_item)
            self.db.commit()
            self.db.refresh(wishlist_item)
            return wishlist_item
        except Exception:
            self.db.rollback()
            return None

    def remove_from_wishlist(self, user_id: int, plate_id: int) -> bool:
        """Remove a license plate from user's wishlist"""
        wishlist_item = self.db.query(WishlistItem).filter(
            WishlistItem.user_id == user_id,
            WishlistItem.plate_id == plate_id
        ).first()
        
        if wishlist_item:
            self.db.delete(wishlist_item)
            self.db.commit()
            return True
        return False

    def get_wishlist(self, user_id: int) -> List[LicensePlate]:
        """Get all license plates in user's wishlist"""
        wishlist_items = self.db.query(WishlistItem).filter(
            WishlistItem.user_id == user_id
        ).all()
        
        return [item.plate for item in wishlist_items]

    def is_in_wishlist(self, user_id: int, plate_id: int) -> bool:
        """Check if a license plate is in user's wishlist"""
        return self.db.query(WishlistItem).filter(
            WishlistItem.user_id == user_id,
            WishlistItem.plate_id == plate_id
        ).first() is not None 