import paypalrestsdk
from sqlalchemy.orm import Session
from models import Order, OrderStatus, LicensePlate, User
from datetime import datetime
from services.email_service import EmailService
from typing import Dict, Any

class PayPalService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
        
        # Configure PayPal SDK with sandbox credentials
        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": "AXTwuceoJm4yTCbB6QXZieKqfGBKs8MDkzSLQRFgZS9KD9bnI7RomoEwjKgZba1Hp-4sKk8JvQeyCS7g",
            "client_secret": "EKlnyvqAMScWWp0j9ZrxiUx0Rx7bvb4Lx_yEBm_EquQxxtgUNS_biLa6l4ZF1x_-QRzWJr3It_22OvdS"
        })

    def create_payment(self, order_id: int) -> Dict[str, Any]:
        """
        Create a PayPal payment for an order
        Returns the payment object with approval URL
        """
        # Get the order
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")

        # Get the plate
        plate = self.db.query(LicensePlate).filter(LicensePlate.plateID == order.plate_id).first()
        if not plate:
            raise ValueError("Plate not found")

        # Check if plate is already sold
        if plate.is_sold:
            raise ValueError("Plate is already sold")

        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"http://localhost:8000/payment/success/{order_id}",
                "cancel_url": f"http://localhost:8000/payment/cancel/{order_id}"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"License Plate {plate.plateNumber}{plate.plateLetter}",
                        "sku": f"plate-{plate.plateID}",
                        "price": str(order.price),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(order.price),
                    "currency": "USD"
                },
                "description": f"Purchase of license plate {plate.plateNumber}{plate.plateLetter}"
            }]
        })

        if payment.create():
            # Store payment ID in order for later reference
            order.payment_id = payment.id
            self.db.commit()
            
            # Return approval URL
            for link in payment.links:
                if link.method == "REDIRECT":
                    return {
                        "payment_id": payment.id,
                        "approval_url": link.href
                    }
        else:
            print("PayPal Error:", payment.error)  # Add error logging
        
        raise ValueError("Failed to create PayPal payment")

    def execute_payment(self, payment_id: str, payer_id: str) -> bool:
        """
        Execute a PayPal payment after user approval
        Returns True if payment is successful, False otherwise
        """
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Get the order associated with this payment
            order = self.db.query(Order).filter(Order.payment_id == payment_id).first()
            if not order:
                return False

            # Get the plate
            plate = self.db.query(LicensePlate).filter(LicensePlate.plateID == order.plate_id).first()
            if not plate:
                return False

            try:
                # Mark the plate as sold
                plate.is_sold = True
                
                # Update order status to in progress
                order.status = OrderStatus.IN_PROGRESS
                order.updated_at = datetime.utcnow()
                
                # Get buyer and seller info
                buyer = self.db.query(User).filter(User.id == order.buyer_id).first()
                seller = self.db.query(User).filter(User.id == order.seller_id).first()

                # Send emails to buyer and seller
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
                
                # Commit all changes
                self.db.commit()
                return True
                
            except Exception as e:
                # If payment fails, rollback any changes
                self.db.rollback()
                print(f"Payment execution failed: {str(e)}")
                return False
        
        return False 