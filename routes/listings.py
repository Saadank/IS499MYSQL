from fastapi import APIRouter, Request, Form, Depends, File, UploadFile, status, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from dependencies import require_auth, get_current_user
from typing import Optional
from services.license_plate_service import LicensePlateService
from services.session_service import SessionService
from models import User, Order, OrderStatus, LicensePlate
from utils.template_config import templates
from services.wishlist_service import WishlistService
from datetime import datetime, timedelta
from services.order_service import OrderService

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
        price = buy_now_price

        # Create the license plate
        plate, warning = await plate_service.create_listing(
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
            city=city,
            transfer_cost=transfer_cost,
            plate_type=plate_type
        )
        
        if warning:
            # Return to the form with the warning message
            template_data = plate_service.get_add_listing_data(request)
            template_data.update({
                "warning": warning,
                "digit1": digit1,
                "digit2": digit2,
                "digit3": digit3,
                "digit4": digit4,
                "letter1": letter1,
                "letter2": letter2,
                "letter3": letter3,
                "description": description,
                "price": price,
                "city": city,
                "plate_type": plate_type
            })
            return templates.TemplateResponse("addlisting.html", template_data, status_code=400)
        
        return RedirectResponse(url="/seller-control-panel", status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        # For unexpected errors, return to form with error message
        plate_service = LicensePlateService(db)
        template_data = plate_service.get_add_listing_data(request)
        template_data.update({
            "error": f"Error creating listing: {str(e)}",
            "digit1": digit1,
            "digit2": digit2,
            "digit3": digit3,
            "digit4": digit4,
            "letter1": letter1,
            "letter2": letter2,
            "letter3": letter3,
            "description": description,
            "price": price,
            "city": city,
            "plate_type": plate_type
        })
        return templates.TemplateResponse("addlisting.html", template_data, status_code=500)

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
    digit1: Optional[str] = Query(None, min_length=0, max_length=1, regex="^[0-9x]?$"),
    digit2: Optional[str] = Query(None, min_length=0, max_length=1, regex="^[0-9x]?$"),
    digit3: Optional[str] = Query(None, min_length=0, max_length=1, regex="^[0-9x]?$"),
    digit4: Optional[str] = Query(None, min_length=0, max_length=1, regex="^[0-9x]?$"),
    letter1: Optional[str] = Query(None),
    letter2: Optional[str] = Query(None),
    letter3: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("newest", regex="^(newest|oldest|price_high|price_low)$"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user)
):
    """
    Handle the for sale page with search functionality.
    - Digits must be single numbers or 'x'
    - Letters are validated against valid letter list
    - Sort options are validated
    """
    session_service = SessionService(request)
    plate_service = LicensePlateService(db)
    
    # Clean and validate letter inputs
    cleaned_letters = []
    valid_letters = set(plate_service.VALID_LETTERS + ['ANY'])
    for letter in [letter1, letter2, letter3]:
        if letter and letter.strip():
            upper_letter = letter.strip().upper()
            if upper_letter != 'ANY' and upper_letter not in valid_letters:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid letter: {letter}. Valid letters are: {', '.join(plate_service.VALID_LETTERS)}"
                )
            cleaned_letters.append(upper_letter)
        else:
            cleaned_letters.append(None)
    
    # Get the search results and template data
    plate_data = plate_service.get_forsale_data(
        request=request,
        digit1=digit1.strip() if digit1 and digit1.strip() else None,
        digit2=digit2.strip() if digit2 and digit2.strip() else None,
        digit3=digit3.strip() if digit3 and digit3.strip() else None,
        digit4=digit4.strip() if digit4 and digit4.strip() else None,
        letter1=cleaned_letters[0],
        letter2=cleaned_letters[1],
        letter3=cleaned_letters[2],
        sort_by=sort_by
    )
    
    template_data = session_service.get_template_data(plate_data)
    
    return templates.TemplateResponse("forsale.html", template_data)

@router.delete("/plates/{plate_id}")
async def delete_plate(
    plate_id: int,
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db)
):
    plate_service = LicensePlateService(db)
    if await plate_service.delete_license_plate(plate_id, user_id):
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
    
    # Get user object if logged in
    user = None
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
    
    template_data = session_service.get_template_data({
        "plate": plate,
        "is_in_wishlist": is_in_wishlist,
        "letter_english": plate_service.LETTER_ENGLISH,
        "user": user,
        "username": user.username if user else None
    })
    
    return templates.TemplateResponse("plate_details.html", template_data)

@router.post("/buy-now/{plate_id}")
async def buy_now(
    request: Request, 
    plate_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get the plate
    plate = db.query(LicensePlate).filter(LicensePlate.plateID == plate_id).first()
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    
    # Check if user is trying to buy their own plate
    if plate.owner_id == user.id:
        raise HTTPException(status_code=400, detail="You cannot buy your own plate")
    
    # Check if plate is already sold
    if plate.is_sold:
        raise HTTPException(status_code=400, detail="This plate has already been sold")
    
    # Clean up any expired orders
    order_service = OrderService(db)
    order_service.cleanup_expired_orders()
    
    # Check if there's already a pending order for this plate
    existing_order = db.query(Order).filter(
        Order.plate_id == plate_id,
        Order.status == OrderStatus.PENDING
    ).first()
    
    if existing_order:
        raise HTTPException(status_code=400, detail="This plate is already in a pending order")
    
    # Create a new order
    order = Order(
        plate_id=plate_id,
        buyer_id=user.id,
        seller_id=plate.owner_id,
        price=plate.price,
        status=OrderStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=1)
    )
    
    db.add(order)
    db.commit()
    
    # Redirect to payment page
    return {"redirect_url": f"/payment/{order.id}"}

@router.get("/seller-control-panel", response_class=HTMLResponse)
async def seller_control_panel(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    plate_service = LicensePlateService(db)
    session_service = SessionService(request)
    
    # Query all plates owned by the current user
    plates = db.query(LicensePlate).filter(LicensePlate.owner_id == user_id).all()
    
    # For each plate, get the buyer information if sold
    for plate in plates:
        if plate.is_sold:
            order = db.query(Order).filter(
                Order.plate_id == plate.plateID,
                Order.status == OrderStatus.COMPLETED
            ).first()
            if order:
                plate.buyer = db.query(User).filter(User.id == order.buyer_id).first()
                plate.sale_date = order.updated_at
        else:
            plate.buyer = None
            plate.sale_date = None
    
    template_data = session_service.get_template_data({
        "plates": plates,
        "letter_english": plate_service.LETTER_ENGLISH,
        "letter_arabic": plate_service.LETTER_ARABIC
    })
    
    return templates.TemplateResponse("seller_control_panel.html", template_data)

@router.post("/plate/{plate_id}/update")
async def update_plate_details(
    plate_id: int,
    request: Request,
    price: float = Form(...),
    city: str = Form(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    plate_service = LicensePlateService(db)
    
    # Get the plate and verify ownership
    plate = db.query(LicensePlate).filter(
        LicensePlate.plateID == plate_id,
        LicensePlate.owner_id == user_id
    ).first()
    
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found or you don't have permission to edit it")
    
    # Update the plate details
    plate.price = price
    plate.city = city
    
    db.commit()
    return RedirectResponse(url="/seller-control-panel", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/plate/{plate_id}/edit", response_class=HTMLResponse)
async def edit_plate_page(
    request: Request,
    plate_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    plate_service = LicensePlateService(db)
    session_service = SessionService(request)
    
    # Get the plate and verify ownership
    plate = db.query(LicensePlate).filter(
        LicensePlate.plateID == plate_id,
        LicensePlate.owner_id == user_id
    ).first()
    
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found or you don't have permission to edit it")
    
    template_data = session_service.get_template_data({
        "plate": plate
    })
    
    return templates.TemplateResponse("edit_plate.html", template_data) 