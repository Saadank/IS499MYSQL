from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, UniqueConstraint, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timedelta, UTC

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
    license_plates = relationship("LicensePlate", back_populates="owner")

class LicensePlate(Base):
    __tablename__ = "license_plates"

    plateID = Column(Integer, primary_key=True, index=True)
    plateNumber = Column(String(4), nullable=False, index=True)
    plateLetter = Column(String(4), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)    
    image_path = Column(String(255), nullable=True)  # Store the path to the image
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="license_plates")

    __table_args__ = (
        UniqueConstraint('plateNumber', 'plateLetter', name='unique_plate_combination'),
        CheckConstraint("plateNumber REGEXP '^[0-9]{4}$'", name='plate_number_format'),
        CheckConstraint("plateLetter REGEXP '^[A-Za-z]{1,4}$'", name='plate_letter_format'),
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