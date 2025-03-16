from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

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
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with license plates
    license_plates = relationship("LicensePlate", back_populates="owner")

class LicensePlate(Base):
    __tablename__ = "license_plates"

    plateID = Column(Integer, primary_key=True, index=True)
    plateNumber = Column(String(4), nullable=False, index=True)
    plateLetter = Column(String(4), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="license_plates")

    __table_args__ = (
        UniqueConstraint('plateNumber', 'plateLetter', name='unique_plate_combination'),
        CheckConstraint("plateNumber REGEXP '^[0-9]{4}$'", name='plate_number_format'),
        CheckConstraint("plateLetter REGEXP '^[A-Za-z]{1,4}$'", name='plate_letter_format'),
    ) 