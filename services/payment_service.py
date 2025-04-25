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
            
        # Get the order
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False

        # Get the plate
        plate = self.db.query(LicensePlate).filter(LicensePlate.plateID == order.plate_id).first()
        if not plate:
            return False

        # Check if plate is already sold
        if plate.is_sold:
            return False

        # Simulate payment processing
        # In a real application, this would call a payment gateway
        try:
            # If payment is successful:
            # 1. Mark the plate as sold
            plate.is_sold = True
            
            # 2. Update order status to completed
            order.status = OrderStatus.COMPLETED
            order.updated_at = datetime.utcnow()
            
            # 3. Get buyer and seller info
            buyer = self.db.query(User).filter(User.id == order.buyer_id).first()
            seller = self.db.query(User).filter(User.id == order.seller_id).first()

            # 4. Send emails to buyer and seller
            buyer_info = {
                'name': buyer.username,
                'email': buyer.email,
                'phone_number': buyer.phone_number
            }
            seller_info = {
                'name': seller.username,
                'email': seller.email,
                'phone_number': seller.phone_number
            }
            plate_info = {
                'number': plate.plateNumber,
                'letter': plate.plateLetter,
                'price': plate.price
            }
            self.email_service.send_purchase_notification(buyer_info, seller_info, plate_info)
            
            # 5. Commit all changes
            self.db.commit()
            return True
            
        except Exception as e:
            # If payment fails, rollback any changes
            self.db.rollback()
            print(f"Payment failed: {str(e)}")
            return False 