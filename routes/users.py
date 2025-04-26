from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import UserService
from services.session_service import SessionService
from dependencies import require_auth
from services.auth_service import get_current_user, verify_password, get_password_hash
from models import User, Order
from utils.template_config import templates
from services.license_plate_service import LicensePlateService
from services.order_service import OrderService

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
    
    # Define the letter mapping
    letter_english = {
        'أ': 'A', 'ب': 'B', 'س': 'C', 'د': 'D', 'ع': 'E',
        'ف': 'F', 'ج': 'G', 'ح': 'H', 'ي': 'I', 'ك': 'K',
        'ل': 'L', 'م': 'M', 'ن': 'N', 'و': 'O', 'ق': 'Q',
        'ر': 'R', 'ت': 'T', 'ز': 'Z'
    }
    
    # Add letter mapping to user data
    user_data['letter_english'] = letter_english
    
    template_data = session_service.get_template_data(user_data)
    
    return templates.TemplateResponse("profile.html", template_data)

@router.get("/order-history", response_class=HTMLResponse, name="order_history")
async def order_history(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    session_service = SessionService(request)
    order_service = OrderService(db)
    
    # Clean up any expired orders
    order_service.cleanup_expired_orders()
    
    # Get user's orders
    orders = order_service.get_user_orders(user_id)
    
    # Separate purchases and sales
    purchases = [order for order in orders if order.buyer_id == user_id]
    sales = [order for order in orders if order.seller_id == user_id]
    
    template_data = session_service.get_template_data({
        "purchases": purchases,
        "sales": sales
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

@router.get("/buyer/{buyer_id}", response_class=HTMLResponse)
async def buyer_details(
    request: Request,
    buyer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get the buyer
    buyer = db.query(User).filter(User.id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    session_service = SessionService(request)
    template_data = session_service.get_template_data({"buyer": buyer})

    # If user is admin, show full details including purchase history
    if current_user.is_admin:
        # Get buyer's purchase history
        purchases = (
            db.query(Order)
            .filter(Order.buyer_id == buyer_id)
            .order_by(Order.created_at.desc())
            .all()
        )
        template_data["purchases"] = purchases
        return templates.TemplateResponse("buyer_details.html", template_data)
    else:
        # For sellers, show limited information
        return templates.TemplateResponse("buyer_details_seller.html", template_data)

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all users
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    session_service = SessionService(request)
    template_data = session_service.get_template_data({
        "users": users
    })
    
    return templates.TemplateResponse("admin/users.html", template_data)

@router.post("/admin/users/{user_id}/toggle-ban")
async def toggle_user_ban(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Toggle ban status
    user.is_banned = not user.is_banned
    db.commit()
    
    return {"success": True, "is_banned": user.is_banned}

@router.delete("/admin/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting admin users
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    try:
        # Delete user's orders
        db.query(Order).filter(
            (Order.buyer_id == user_id) | (Order.seller_id == user_id)
        ).delete(synchronize_session=False)
        
        # Delete the user
        db.delete(user)
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-phone")
async def update_phone(
    phone_number: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        user_service = UserService(db)
        user_service.update_user_phone(current_user.id, phone_number)
        return JSONResponse(content={"message": "Phone number updated successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-iban")
async def update_iban(
    iban: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        user_service = UserService(db)
        user_service.update_user_iban(current_user.id, iban)
        return JSONResponse(content={"message": "IBAN updated successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-password")
async def update_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify current password
    if not verify_password(current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    try:
        user_service = UserService(db)
        hashed_password = get_password_hash(new_password)
        user_service.update_user_password(current_user.id, hashed_password)
        return JSONResponse(content={"message": "Password updated successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 