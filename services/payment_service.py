from sqlalchemy.orm import Session
from models import Order, OrderStatus, LicensePlate, User
from datetime import datetime
from services.email_service import EmailService

class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()

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
        
        # Get buyer and seller info
        buyer = self.db.query(User).filter(User.id == order.buyer_id).first()
        seller = self.db.query(User).filter(User.id == order.seller_id).first()

        # Send emails to buyer and seller
        buyer_info = {
            'name': buyer.username,
            'email': buyer.email
        }
        seller_info = {
            'name': seller.username,
            'email': seller.email
        }
        plate_info = {
            'number': plate.plateNumber,
            'letter': plate.plateLetter,
            'price': plate.price
        }
        self.email_service.send_purchase_notification(buyer_info, seller_info, plate_info)
        
        return True 