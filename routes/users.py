from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import UserService
from services.session_service import SessionService
from dependencies import require_auth
from services.auth_service import get_current_user
from models import User
from utils.template_config import templates
from services.license_plate_service import LicensePlateService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile", response_class=HTMLResponse, name="profile_page")
async def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    session_service = SessionService(request)
    user_service = UserService(db)
    
    user_data = user_service.get_user_profile_data(user_id)
    
    # Use the standardized letter mapping from LicensePlateService
    letter_english = LicensePlateService.LETTER_ENGLISH
    letter_arabic = LicensePlateService.LETTER_ARABIC
    
    # Add letter mapping to user data
    user_data['letter_english'] = letter_english
    user_data['letter_arabic'] = letter_arabic
    
    template_data = session_service.get_template_data(user_data)
    
    return templates.TemplateResponse("profile.html", template_data)

@router.get("/order-history", response_class=HTMLResponse, name="order_history")
async def order_history(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_service = SessionService(request)
    user_service = UserService(db)
    orders = user_service.get_user_orders(current_user.id)
    
    template_data = session_service.get_template_data({
        "purchases": orders["purchases"],
        "sales": orders["sales"]
    })
    
    return templates.TemplateResponse("order-history.html", template_data)

@router.get("/active-offers", response_class=HTMLResponse, name="active_offers")
async def active_offers(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_service = SessionService(request)
    user_service = UserService(db)
    
    # Get both sent and received offers
    offers = user_service.get_user_offers(current_user.id)
    
    template_data = session_service.get_template_data({
        "sent_offers": offers["sent"],
        "received_offers": offers["received"]
    })
    
    return templates.TemplateResponse("active_offers.html", template_data) 