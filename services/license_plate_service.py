from sqlalchemy.orm import Session
from typing import List, Optional
from models import LicensePlate
from datetime import datetime
from services.file_service import FileService
from fastapi import UploadFile

class LicensePlateService:
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()

    async def create_license_plate(
        self,
        plate_number: str,
        plate_letter: str,
        description: str,
        price: float,
        owner_id: int,
        image: Optional[UploadFile] = None
    ) -> LicensePlate:
        image_path = None
        if image:
            image_path = await self.file_service.save_image(image)

        db_plate = LicensePlate(
            plateNumber=plate_number,
            plateLetter=plate_letter,
            description=description,
            price=price,
            owner_id=owner_id,
            image_path=image_path
        )
        self.db.add(db_plate)
        self.db.commit()
        self.db.refresh(db_plate)
        return db_plate

    def get_license_plates(self, skip: int = 0, limit: int = 100) -> List[LicensePlate]:
        return self.db.query(LicensePlate).offset(skip).limit(limit).all()

    def get_license_plate(self, plate_id: int) -> Optional[LicensePlate]:
        return self.db.query(LicensePlate).filter(LicensePlate.plateID == plate_id).first()

    def get_user_license_plates(self, user_id: int) -> List[LicensePlate]:
        return self.db.query(LicensePlate).filter(LicensePlate.owner_id == user_id).all()

    async def update_license_plate(
        self,
        plate_id: int,
        plate_number: Optional[str] = None,
        plate_letter: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        image: Optional[UploadFile] = None
    ) -> Optional[LicensePlate]:
        plate = self.get_license_plate(plate_id)
        if not plate:
            return None

        if plate_number:
            plate.plateNumber = plate_number
        if plate_letter:
            plate.plateLetter = plate_letter
        if description:
            plate.description = description
        if price:
            plate.price = price

        if image:
            # Delete old image if it exists
            if plate.image_path:
                self.file_service.delete_image(plate.image_path)
            # Save new image
            plate.image_path = await self.file_service.save_image(image)

        self.db.commit()
        self.db.refresh(plate)
        return plate

    def delete_license_plate(self, plate_id: int, user_id: int) -> bool:
        plate = self.get_license_plate(plate_id)
        if not plate or plate.owner_id != user_id:
            return False
        
        # Delete associated image if it exists
        if plate.image_path:
            self.file_service.delete_image(plate.image_path)
        
        self.db.delete(plate)
        self.db.commit()
        return True 