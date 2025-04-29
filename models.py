from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, UniqueConstraint, CheckConstraint, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timedelta, UTC
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

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
    phone_number = Column(String(20), nullable=False)
    iban = Column(String(34))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    
    # Relationships
    plates = relationship("LicensePlate", back_populates="owner", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="user")
    purchases = relationship("Order", foreign_keys="Order.buyer_id", back_populates="buyer")
    sales = relationship("Order", foreign_keys="Order.seller_id", back_populates="seller")

class ListingType(str, Enum):
    BUY_NOW = "buy_now"

class LicensePlate(Base):
    __tablename__ = "license_plates"

    plateID = Column(Integer, primary_key=True, index=True)
    plateNumber = Column(String(4), nullable=False)
    plateLetter = Column(String(3), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    image_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    listing_type = Column(String(20), nullable=False)
    buy_now_price = Column(Float, nullable=True)
    city = Column(String(50))
    transfer_cost = Column(String(50))
    plate_type = Column(String(20))
    is_sold = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)

    # Relationships
    owner = relationship("User", back_populates="plates")

    __table_args__ = (
        CheckConstraint(
            "plateLetter REGEXP '^[A-Z]{1,3}$'",
            name='plate_letter_format'
        ),
        UniqueConstraint('plateNumber', 'plateLetter', 'plate_type', name='unique_plate_number_letter_type'),
    )

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plate_id = Column(Integer, ForeignKey("license_plates.plateID"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    user = relationship("User", back_populates="wishlist_items")
    plate = relationship("LicensePlate", backref="wishlist_items")

    # Ensure unique combination of user and plate
    __table_args__ = (
        UniqueConstraint('user_id', 'plate_id', name='unique_user_plate_wishlist'),
    )

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    plate_id = Column(Integer, ForeignKey("license_plates.plateID"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(SQLAlchemyEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    expires_at = Column(DateTime, default=lambda: datetime.now(UTC) + timedelta(minutes=1))
    payment_id = Column(String(50), nullable=True)  # PayPal payment ID

    # Relationships
    plate = relationship("LicensePlate")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="purchases")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="sales") 