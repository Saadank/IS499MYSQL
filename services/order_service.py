from sqlalchemy.orm import Session
from models import Order, OrderStatus
from datetime import datetime

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def cleanup_expired_orders(self):
        """
        Clean up expired pending orders
        """
        now = datetime.utcnow()
        expired_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.PENDING,
            Order.expires_at < now
        ).all()

        for order in expired_orders:
            # Update order status to cancelled
            order.status = OrderStatus.CANCELLED
            order.updated_at = now

        if expired_orders:
            self.db.commit()
            return len(expired_orders)
        
        return 0

    def get_user_orders(self, user_id: int):
        """
        Get all orders for a user, excluding expired pending orders
        """
        now = datetime.utcnow()
        
        # Get all orders except expired pending ones
        orders = self.db.query(Order).filter(
            (Order.buyer_id == user_id) | (Order.seller_id == user_id),
            ~(
                (Order.status == OrderStatus.PENDING) & 
                (Order.expires_at < now)
            )
        ).order_by(Order.created_at.desc()).all()
        
        return orders 