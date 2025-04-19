import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.email_config import email_settings
from typing import List

class EmailService:
    def __init__(self):
        self.smtp_server = email_settings.SMTP_SERVER
        self.smtp_port = email_settings.SMTP_PORT
        self.username = email_settings.EMAIL_USERNAME
        self.password = email_settings.EMAIL_PASSWORD
        self.email_from = email_settings.EMAIL_FROM

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
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

    def send_purchase_notification(self, to_email: str, plate_number: str, amount: float) -> bool:
        subject = "License Plate Purchase Confirmation"
        body = f"""
        <html>
            <body>
                <h2>Purchase Confirmation</h2>
                <p>Thank you for your purchase!</p>
                <p>License Plate: {plate_number}</p>
                <p>Amount: {amount} SAR</p>
                <p>Please log in to your account to view the details of your purchase.</p>
                <br>
                <p>Best regards,<br>License Plate Trading Team</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, body) 