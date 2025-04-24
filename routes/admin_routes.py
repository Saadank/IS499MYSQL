from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, LicensePlate, Order
from schemas import UserResponse, LicensePlateResponse
from routes.auth import get_current_user
from utils.template_config import templates
from services.email_service import EmailService

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def verify_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform admin actions"
        )
    return current_user

@router.get("", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Admin dashboard page"""
    # Get total users count
    total_users = db.query(User).count()
    
    # Get active listings count (not sold and approved)
    active_listings = db.query(LicensePlate).filter(
        LicensePlate.is_sold == False,
        LicensePlate.is_approved == True
    ).count()
    
    # Get recent activities (last 5 orders)
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
    recent_activities = [
        {
            "description": f"Order #{order.id} created by user {order.buyer_id}",
            "timestamp": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for order in recent_orders
    ]
    
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "total_users": total_users,
            "active_listings": active_listings,
            "recent_activities": recent_activities
        }
    )

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Admin users management page"""
    users = db.query(User).all()
    return templates.TemplateResponse(
        "admin_users.html",
        {"request": request, "users": users}
    )

@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Ban a user from the system"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete all user's license plates
    plates = db.query(LicensePlate).filter(LicensePlate.owner_id == user_id).all()
    for plate in plates:
        db.delete(plate)
    
    # Ban the user
    user.is_banned = True
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Delete a user from the system"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/users/{user_id}/details", response_class=HTMLResponse)
async def view_user_details(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """View detailed information about a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Load the user's purchases
    purchases = db.query(Order).filter(Order.buyer_id == user_id).order_by(Order.created_at.desc()).all()
    user.purchases = purchases
    
    return templates.TemplateResponse(
        "user_details.html",
        {"request": request, "user": user}
    )

@router.get("/license-plates", response_class=HTMLResponse)
async def admin_license_plates(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Admin license plates management page"""
    plates = db.query(LicensePlate).all()
    return templates.TemplateResponse(
        "admin_license_plates.html",
        {"request": request, "plates": plates}
    )

@router.post("/license-plates/{plate_id}")
async def delete_license_plate(
    plate_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Delete a license plate from the system"""
    plate = db.query(LicensePlate).filter(LicensePlate.plateID == plate_id).first()
    if not plate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License plate not found"
        )
    db.delete(plate)
    db.commit()
    return RedirectResponse(url="/admin/license-plates", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/license-plates/{plate_id}/approve")
async def approve_license_plate(
    plate_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Approve a license plate"""
    plate = db.query(LicensePlate).filter(LicensePlate.plateID == plate_id).first()
    if not plate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License plate not found"
        )
    
    plate.is_approved = True
    db.commit()
    
    # Send approval email
    user = db.query(User).filter(User.id == plate.owner_id).first()
    if user:
        email_service = EmailService()
        email_service.send_listing_approved_email(user, plate)
    
    return RedirectResponse(url="/admin/license-plates", status_code=status.HTTP_303_SEE_OTHER) 