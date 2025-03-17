from fastapi import APIRouter, Request, Form, Depends, File, UploadFile, status, Query
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
from typing import Optional

router = APIRouter(prefix="", tags=["listings"])
templates = Jinja2Templates(directory="templates")
file_service = FileService()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Valid Arabic letters excluding the specified ones
VALID_LETTERS = [
    'ا', 'ب', 'ج', 'د', 'ر', 'س', 'ص', 'ط', 'ع', 'ف', 'ق', 'ل', 'م', 'ن', 'ه', 'و', 'ي'
]

# English letter mappings for Arabic letters
LETTER_ENGLISH = {
    'ا': 'A', 'ب': 'B', 'ج': 'J', 'د': 'D', 'ر': 'R', 'س': 'S', 'ص': 'S', 'ط': 'T',
    'ع': 'A', 'ف': 'F', 'ق': 'Q', 'ل': 'L', 'م': 'M', 'ن': 'N', 'ه': 'H', 'و': 'W', 'ي': 'Y'
}

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
    plate_number: str = Form(...),
    plate_letter: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    # Validate input using schema
    plate_data = LicensePlateCreate(
        plateNumber=plate_number,
        plateLetter=plate_letter,
        description=description,
        price=price
    )
    
    # Create license plate using service
    plate_service = LicensePlateService(db)
    plate = plate_service.create_license_plate(
        plate_number=plate_data.plateNumber,
        plate_letter=plate_data.plateLetter,
        description=plate_data.description,
        price=plate_data.price,
        owner_id=user_id
    )
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

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

@router.get("/forsale", response_class=HTMLResponse)
async def for_sale_page(
    request: Request,
    digit1: Optional[str] = Query(None),
    digit2: Optional[str] = Query(None),
    digit3: Optional[str] = Query(None),
    digit4: Optional[str] = Query(None),
    letter1: Optional[str] = Query(None),
    letter2: Optional[str] = Query(None),
    letter3: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("newest"),
    db: Session = Depends(get_db)
):
    plate_service = LicensePlateService(db)
    
    # Get plates with filters
    plates = plate_service.get_license_plates()
    
    # Apply filters
    if any([digit1, digit2, digit3, digit4]):
        filtered_plates = []
        for plate in plates:
            plate_digits = [int(d) for d in plate.plateNumber]
            # Check if the plate number matches the provided digits up to the length of the plate number
            matches = True
            for i, digit in enumerate([digit1, digit2, digit3, digit4]):
                if digit == 'x':
                    # If X is selected, the plate should have fewer digits than this position
                    if i < len(plate_digits):
                        matches = False
                        break
                elif digit is not None:
                    # If a specific digit is selected, it should match
                    if i >= len(plate_digits) or plate_digits[i] != int(digit):
                        matches = False
                        break
            if matches:
                filtered_plates.append(plate)
        plates = filtered_plates

    if any([letter1, letter2, letter3]):
        filtered_plates = []
        for plate in plates:
            plate_letters = list(plate.plateLetter)
            if (not letter1 or plate_letters[0] == letter1) and \
               (not letter2 or len(plate_letters) > 1 and plate_letters[1] == letter2) and \
               (not letter3 or len(plate_letters) > 2 and plate_letters[2] == letter3):
                filtered_plates.append(plate)
        plates = filtered_plates
    
    # Apply sorting
    if sort_by == "newest":
        plates.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "oldest":
        plates.sort(key=lambda x: x.created_at)
    elif sort_by == "price_high":
        plates.sort(key=lambda x: x.price, reverse=True)
    elif sort_by == "price_low":
        plates.sort(key=lambda x: x.price)
    
    return templates.TemplateResponse("forsale.html", {
        "request": request,
        "plates": plates,
        "digit1": digit1,
        "digit2": digit2,
        "digit3": digit3,
        "digit4": digit4,
        "letter1": letter1,
        "letter2": letter2,
        "letter3": letter3,
        "sort_by": sort_by,
        "valid_letters": VALID_LETTERS,
        "letter_english": LETTER_ENGLISH
    }) 