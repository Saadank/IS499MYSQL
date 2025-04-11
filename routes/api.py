from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from services.license_plate_service import LicensePlateService
from typing import Optional
from models import User
from services.auth_service import AuthService

router = APIRouter()

@router.get("/api/plates/{plate_id}")
async def get_plate_details(
    plate_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user)
):
    try:
        plate_service = LicensePlateService(db)
        plate = plate_service.get_plate_details(plate_id)
        
        if not plate:
            raise HTTPException(status_code=404, detail="Plate not found")
        
        # Get username if user is logged in
        username = None
        if user_id:
            auth_service = AuthService(db)
            user = auth_service.get_user(user_id)
            if user:
                username = user.username
        
        return {
            "plate": {
                "plateID": plate.plateID,
                "plate_number": plate.plate_number,
                "city": plate.city,
                "created_at": plate.created_at.isoformat() if plate.created_at else None,
                "price": float(plate.price) if plate.price else 0,
                "transfer_cost": plate.transfer_cost,
                "plate_type": plate.plate_type,
                "plateLetter": plate.plate_letter
            },
            "username": username
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 