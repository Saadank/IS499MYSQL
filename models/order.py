from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class OrderStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    plate_id = Column(Integer, ForeignKey("license_plates.plateID"))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    plate = relationship("LicensePlate")

    def to_dict(self):
        return {
            "id": self.id,
            "buyer": {
                "id": self.buyer.id,
                "username": self.buyer.username,
                "email": self.buyer.email
            },
            "seller": {
                "id": self.seller.id,
                "username": self.seller.username,
                "email": self.seller.email
            },
            "plate": {
                "id": self.plate.plateID,
                "number": self.plate.plate_number,
                "letter": self.plate.plate_letter,
                "price": self.plate.price
            },
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        } 