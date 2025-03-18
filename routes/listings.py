from fastapi import APIRouter, Request, Form, Depends, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from dependencies import require_auth

from services.file_service import FileService
from .schemas import LicensePlateCreate
import os
from datetime import datetime
from services.license_plate_service import LicensePlateService

router = APIRouter(prefix="", tags=["listings"])
templates = Jinja2Templates(directory="templates")
file_service = FileService()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/addlisting", response_class=HTMLResponse)
async def add_plate_page(
    request: Request,
    user_id: int = Depends(require_auth)
):
    return templates.TemplateResponse("addlisting.html", {
        "request": request,
        "username": request.session.get("username")
    })

@router.post("/addlisting")
async def create_listing(
    request: Request,
    plateNumber: str = Form(...),
    plateLetter: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    plate_service = LicensePlateService(db)
    
    # Create the license plate with image
    plate = await plate_service.create_license_plate(
        plate_number=plateNumber,
        plate_letter=plateLetter,
        description=description,
        price=price,
        owner_id=user_id,
        image=image
    )
    
    return RedirectResponse(url="/plates", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/plates", response_class=HTMLResponse)
async def list_plates(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    plate_service = LicensePlateService(db)
    plates = plate_service.get_license_plates()
    return templates.TemplateResponse("plates.html", {
        "request": request,
        "plates": plates,
        "username": request.session.get("username")
    }) 