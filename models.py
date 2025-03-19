from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, UniqueConstraint, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timedelta, UTC
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))
    firstname = Column(String(50))
    lastname = Column(String(50))
    idnumber = Column(String(20), unique=True)
    address = Column(String(200))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Relationship with license plates
    plates = relationship("LicensePlate", back_populates="owner")
    offers = relationship("Offer", back_populates="user")

class ListingType(str, Enum):
    BUY_NOW = "buy_now"
    AUCTION = "auction"
    OFFERS = "offers"

class LicensePlate(Base):
    __tablename__ = "license_plates"

    plateID = Column(Integer, primary_key=True, index=True)
    plateNumber = Column(String(4), nullable=False)
    plateLetter = Column(String(3), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    listing_type = Column(String(20), nullable=False)
    buy_now_price = Column(Float, nullable=True)
    auction_start_price = Column(Float, nullable=True)
    minimum_offer_price = Column(Float, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="plates")
    offers = relationship("Offer", back_populates="plate")

    __table_args__ = (
        CheckConstraint(
            "plateLetter REGEXP '^[ابجدرسصطعفقلمنهوي]{1,3}$'",
            name='plate_letter_format'
        ),
        UniqueConstraint('plateNumber', 'plateLetter', name='unique_plate_number_letter'),
    ) 

class Auction(Base):
    __tablename__ = "auctions"

    id = Column(Integer, primary_key=True, index=True)
    plate_id = Column(Integer, ForeignKey("license_plates.plateID"), nullable=False)
    start_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    start_time = Column(DateTime, default=lambda: datetime.now(UTC))
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    plate = relationship("LicensePlate", backref="auctions")
    winner = relationship("User", backref="won_auctions")
    bids = relationship("Bid", back_populates="auction")

class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Relationships
    auction = relationship("Auction", back_populates="bids")
    user = relationship("User", backref="bids")

class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_id = Column(Integer, ForeignKey("license_plates.plateID"))
    user_id = Column(Integer, ForeignKey("users.id"))
    offer_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # Added length specification
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plate = relationship("LicensePlate", back_populates="offers")
    user = relationship("User", back_populates="offers") 