from sqlalchemy.orm import Session
from models import Order, OrderStatus, LicensePlate
from datetime import datetime

class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def process_payment(self, order_id: int, card_number: str, expiry_date: str, cvv: str) -> bool:
        """
        Process a fake payment for an order
        Returns True if payment is successful, False otherwise
        """
        # In a real application, this would integrate with a payment gateway
        # For demo purposes, we'll just simulate a successful payment
        
        # Basic validation of card details
        if not all([card_number, expiry_date, cvv]):
            return False
            
        # Update order status
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
            
        # Mark the plate as sold
        plate = self.db.query(LicensePlate).filter(LicensePlate.plateID == order.plate_id).first()
        if plate:
            plate.is_sold = True
            
        order.status = OrderStatus.COMPLETED
        order.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True 