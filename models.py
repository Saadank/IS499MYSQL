from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with listings
    listings = relationship("Listing", back_populates="owner")

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(20), index=True)
    description = Column(Text)
    price = Column(Float)
    listing_type = Column(String(20))  # 'auction' or 'sale'
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="listings") 