from fastapi import APIRouter, Request, Form, Depends, File, UploadFile, status, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from dependencies import require_auth, get_current_user
from typing import Optional
from services.license_plate_service import LicensePlateService
from services.session_service import SessionService
from models import User
from utils.template_config import templates
from services.wishlist_service import WishlistService

router = APIRouter(prefix="", tags=["listings"])

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
    city: str = Form(...),
    transfer_cost: str = Form(...),
    plate_type: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    try:
        plate_service = LicensePlateService(db)
        
        # Calculate the price based on listing type
        price = buy_now_price if listing_type == 'buy_now' else \
               auction_start_price if listing_type == 'auction' else \
               minimum_offer_price

        # Create the license plate
        plate = await plate_service.create_listing(
            digit1=digit1,
            digit2=digit2,
            digit3=digit3,
            digit4=digit4,
            letter1=letter1,
            letter2=letter2,
            letter3=letter3,
            description=description,
            price=price,
            image=image,
            user_id=user_id,
            listing_type=listing_type,
            buy_now_price=buy_now_price,
            auction_start_price=auction_start_price,
            minimum_offer_price=minimum_offer_price,
            city=city,
            transfer_cost=transfer_cost,
            plate_type=plate_type
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
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user)
):
    session_service = SessionService(request)
    plate_service = LicensePlateService(db)
    
    plate_data = plate_service.get_forsale_data(request, digit1, digit2, digit3, digit4,
                                               letter1, letter2, letter3, sort_by)
    
    template_data = session_service.get_template_data(plate_data)
    template_data["letter_english"] = plate_service.LETTER_ENGLISH
    
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

@router.get("/plate/{plate_id}", name="plate_details")
async def view_plate_details(
    request: Request,
    plate_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user)
):
    session_service = SessionService(request)
    plate_service = LicensePlateService(db)
    wishlist_service = WishlistService(db)
    
    plate = plate_service.get_plate_details(plate_id)
    
    if not plate:
        template_data = session_service.get_template_data({
            "error": "Plate not found"
        })
        return templates.TemplateResponse("plate_details.html", template_data)
    
    # Check if plate is in user's wishlist
    is_in_wishlist = False
    if user_id:
        is_in_wishlist = wishlist_service.is_in_wishlist(user_id, plate_id)
    
    template_data = session_service.get_template_data({
        "plate": plate,
        "is_in_wishlist": is_in_wishlist,
        "letter_english": plate_service.LETTER_ENGLISH
    })
    
    return templates.TemplateResponse("plate_details.html", template_data) 