from fastapi import APIRouter, Request, Form, Depends, File, UploadFile, status, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from dependencies import require_auth, get_current_user
from typing import Optional
from services.license_plate_service import LicensePlateService
from services.session_service import SessionService
from models import User

router = APIRouter(prefix="", tags=["listings"])
templates = Jinja2Templates(directory="templates")

@router.get("/addlisting", response_class=HTMLResponse)
async def add_plate_page(
    request: Request,
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db)
):
    plate_service = LicensePlateService(db)
    return templates.TemplateResponse("addlisting.html", plate_service.get_add_listing_data(request))

@router.post("/addlisting")
async def create_listing(
    request: Request,
    digit1: str = Form(...),
    digit2: str = Form(...),
    digit3: str = Form(...),
    digit4: str = Form(...),
    letter1: str = Form(...),
    letter2: str = Form(None),
    letter3: str = Form(None),
    description: str = Form(None),
    listing_type: str = Form(...),
    buy_now_price: int = Form(0),
    auction_start_price: int = Form(0),
    minimum_offer_price: int = Form(0),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    try:
        plate_service = LicensePlateService(db)
        
        # Combine digits into plate number, excluding 'x'
        plate_number = ""
        for digit in [digit1, digit2, digit3, digit4]:
            if digit != 'x':
                plate_number += digit
        
        # Combine letters, excluding empty values
        plate_letter = letter1
        if letter2 and letter2 != '':
            plate_letter += letter2
        if letter3 and letter3 != '':
            plate_letter += letter3

        # Create the license plate
        plate = await plate_service.create_license_plate(
            plate_number=plate_number,
            plate_letter=plate_letter,
            description=description,
            price=buy_now_price if listing_type == 'buy_now' else 
                  auction_start_price if listing_type == 'auction' else 
                  minimum_offer_price,
            listing_type=listing_type,
            buy_now_price=buy_now_price,
            auction_start_price=auction_start_price,
            minimum_offer_price=minimum_offer_price,
            owner_id=user_id,
            image=image
        )
        
        return RedirectResponse(url="/plates", status_code=status.HTTP_303_SEE_OTHER)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating listing: {str(e)}")

@router.get("/plates", response_class=HTMLResponse)
async def list_plates(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    plate_service = LicensePlateService(db)
    return templates.TemplateResponse("plates.html", plate_service.get_plates_data(request))

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
    session_service = SessionService(request)
    plate_service = LicensePlateService(db)
    
    plate_data = plate_service.get_forsale_data(request, digit1, digit2, digit3, digit4,
                                               letter1, letter2, letter3, sort_by)
    
    template_data = session_service.get_template_data(plate_data)
    
    return templates.TemplateResponse("forsale.html", template_data)

@router.delete("/plates/{plate_id}")
async def delete_plate(
    plate_id: int,
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db)
):
    plate_service = LicensePlateService(db)
    if plate_service.delete_license_plate(plate_id, user_id):
        return {"message": "Plate removed successfully"}
    raise HTTPException(status_code=400, detail="Failed to remove plate")

@router.get("/plate/{plate_id}", response_class=HTMLResponse)
async def plate_details(
    request: Request,
    plate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        session_service = SessionService(request)
        plate_service = LicensePlateService(db)
        plate_data = plate_service.get_plate_details(plate_id)
        
        if not plate_data:
            template_data = session_service.get_template_data({
                "error": "Plate not found",
                "plate": None,
                "current_user": current_user
            })
            return templates.TemplateResponse("plate_details.html", template_data)
            
        template_data = session_service.get_template_data({
            "plate": plate_data,
            "error": None,
            "current_user": current_user
        })
        return templates.TemplateResponse("plate_details.html", template_data)
    except Exception as e:
        template_data = session_service.get_template_data({
            "error": f"Error loading plate details: {str(e)}",
            "plate": None,
            "current_user": current_user
        })
        return templates.TemplateResponse("plate_details.html", template_data) 