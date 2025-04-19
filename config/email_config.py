from pydantic_settings import BaseSettings

class EmailSettings(BaseSettings):
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USERNAME: str = ""  # Your email address
    EMAIL_PASSWORD: str = ""  # Your email password or app password
    EMAIL_FROM: str = ""  # Sender email address
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # This will ignore extra fields in the .env file

email_settings = EmailSettings() 