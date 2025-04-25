import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.email_config import email_settings
from typing import List, Dict, Optional
import os
from models import User, LicensePlate

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("EMAIL_USERNAME", "your-email@gmail.com")
        self.sender_password = os.getenv("EMAIL_PASSWORD", "your-app-password")

    def send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        subject = "Welcome to License Plate Trading"
        body = f"""
        <html>
            <body>
                <h2>Welcome to License Plate Trading!</h2>
                <p>Dear {username},</p>
                <p>Thank you for registering with us. We're excited to have you on board!</p>
                <p>You can now start browsing and trading license plates.</p>
                <p>If you have any questions, feel free to contact our support team.</p>
                <br>
                <p>Best regards,<br>License Plate Trading Team</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, body)

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        subject = "Password Reset Request"
        reset_link = f"http://yourdomain.com/reset-password?token={reset_token}"
        body = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>We received a request to reset your password.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>If you didn't request this, please ignore this email.</p>
                <p>This link will expire in 1 hour.</p>
                <br>
                <p>Best regards,<br>License Plate Trading Team</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, body)

    def send_offer_notification(self, to_email: str, plate_number: str, offer_amount: float) -> bool:
        subject = "New Offer on Your License Plate"
        body = f"""
        <html>
            <body>
                <h2>New Offer Received</h2>
                <p>You have received a new offer for your license plate {plate_number}.</p>
                <p>Offer Amount: {offer_amount} SAR</p>
                <p>Please log in to your account to view and respond to this offer.</p>
                <br>
                <p>Best regards,<br>License Plate Trading Team</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, body)

    def send_purchase_notification(self, buyer_info: Dict, seller_info: Dict, plate_info: Dict):
        # Email to buyer
        buyer_subject = "License Plate Purchase Confirmation"
        buyer_body = f"""
        <html>
            <body>
                <h2>License Plate Purchase Confirmation</h2>
                <p>Dear {buyer_info['name']},</p>
                
                <p>Thank you for your purchase! Here are the details of your transaction:</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Plate Details</h3>
                    <p>Plate Number: <strong>{plate_info['number']}{plate_info['letter']}</strong></p>
                    <p>Price: <strong>SAR {plate_info['price']}</strong></p>
                </div>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Seller Contact Information</h3>
                    <p>Name: <strong>{seller_info['name']}</strong></p>
                    <p>Email: <strong>{seller_info['email']}</strong></p>
                    <p>Phone: <strong>{seller_info.get('phone_number', 'Not provided')}</strong></p>
                </div>

                <p>Please contact the seller to arrange the transfer of the license plate.</p>
                <br>
                <p>Best regards,<br>License Plate Trading Platform</p>
            </body>
        </html>
        """

        # Email to seller
        seller_subject = "License Plate Sale Confirmation"
        seller_body = f"""
        <html>
            <body>
                <h2>License Plate Sale Confirmation</h2>
                <p>Dear {seller_info['name']},</p>
                
                <p>Your license plate has been sold! Here are the details:</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Plate Details</h3>
                    <p>Plate Number: <strong>{plate_info['number']}{plate_info['letter']}</strong></p>
                    <p>Price: <strong>SAR {plate_info['price']}</strong></p>
                </div>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Buyer Contact Information</h3>
                    <p>Name: <strong>{buyer_info['name']}</strong></p>
                    <p>Email: <strong>{buyer_info['email']}</strong></p>
                    <p>Phone: <strong>{buyer_info.get('phone_number', 'Not provided')}</strong></p>
                </div>

                <p>Please contact the buyer to arrange the transfer of the license plate.</p>
                <br>
                <p>Best regards,<br>License Plate Trading Platform</p>
            </body>
        </html>
        """

        # Send emails
        self.send_email(buyer_info['email'], buyer_subject, buyer_body)
        self.send_email(seller_info['email'], seller_subject, seller_body)

    def send_listing_added_email(self, user: User, plate: LicensePlate) -> bool:
        subject = "Your License Plate Listing Has Been Added"
        body = f"""
        <html>
            <body>
                <h2>Thank you for adding your license plate!</h2>
                <p>Dear {user.username},</p>
                <p>Your license plate listing for <strong>{plate.plateNumber}{plate.plateLetter}</strong> has been successfully added to our system.</p>
                <p>Please note that your listing is currently pending admin approval. This process may take some time.</p>
                <p>You will receive another email once your listing has been approved.</p>
                <p>Thank you for your patience!</p>
                <br>
                <p>Best regards,<br>The License Plate Team</p>
            </body>
        </html>
        """
        return self.send_email(user.email, subject, body)

    def send_listing_approved_email(self, user: User, plate: LicensePlate) -> bool:
        subject = "Your License Plate Listing Has Been Approved"
        body = f"""
        <html>
            <body>
                <h2>Great news! Your license plate has been approved!</h2>
                <p>Dear {user.username},</p>
                <p>Your license plate listing for <strong>{plate.plateNumber}{plate.plateLetter}</strong> has been approved and is now live on our platform.</p>
                <p>You can view your listing at: <a href="/plate/{plate.plateID}">View Listing</a></p>
                <p>Thank you for using our platform!</p>
                <br>
                <p>Best regards,<br>The License Plate Team</p>
            </body>
        </html>
        """
        return self.send_email(user.email, subject, body) 