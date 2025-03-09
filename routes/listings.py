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
async def add_listing_page(
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
    description: str = Form(...),
    price: float = Form(...),
    listing_type: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    # Validate input using schema
    listing_data = ListingCreate(
        plate_number=plate_number,
        description=description,
        price=price,
        listing_type=listing_type
    )
    
    # Handle image upload using file service
    image_path = await file_service.save_image(image)
    
    # Create listing using listing service
    listing_service = ListingService(db)
    listing = listing_service.create_listing(
        plate_number=listing_data.plate_number,
        description=listing_data.description,
        price=listing_data.price,
        listing_type=listing_data.listing_type,
        owner_id=user_id,
        image_path=image_path
    )
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/auction", response_class=HTMLResponse)
async def auction_page(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    listing_service = ListingService(db)
    listings = listing_service.get_listings_by_type("auction")
    return templates.TemplateResponse("auction.html", {
        "request": request,
        "listings": listings,
        "username": request.session.get("username")
    })

@router.get("/forsale", response_class=HTMLResponse)
async def forsale_page(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    listing_service = ListingService(db)
    listings = listing_service.get_listings_by_type("sale")
    return templates.TemplateResponse("forsale.html", {
        "request": request,
        "listings": listings,
        "username": request.session.get("username")
    })

@router.get("/add-plate", response_class=HTMLResponse)
async def add_plate_page(
    request: Request,
    user_id: int = Depends(require_auth)
):
    return templates.TemplateResponse("addlisting.html", {
        "request": request,
        "username": request.session.get("username")
    })

@router.post("/add-plate")
async def create_plate(
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