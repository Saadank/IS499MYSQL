from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from database import get_db
from services.paypal_service import PayPalService
from services.session_service import SessionService
from services.license_plate_service import LicensePlateService
from utils.template_config import templates
from fastapi.responses import HTMLResponse, RedirectResponse
from models import Order, LicensePlate, User
from dependencies import get_current_user, require_auth

router = APIRouter()

@router.get("/payment/{order_id}", response_class=HTMLResponse)
async def payment_page(
    request: Request, 
    order_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    session_service = SessionService(request)
    paypal_service = PayPalService(db)
    
    # Get order details
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify order belongs to user
    if order.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    # Get plate details
    plate = db.query(LicensePlate).filter(LicensePlate.plateID == order.plate_id).first()
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    
    try:
        # Create PayPal payment
        payment = paypal_service.create_payment(order_id)
        
        template_data = session_service.get_template_data({
            "order": order,
            "plate": plate,
            "paypal_approval_url": payment["approval_url"],
            "letter_arabic": LicensePlateService.LETTER_ARABIC
        })
        
        return templates.TemplateResponse("payment.html", template_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payment/success/{order_id}")
async def payment_success(
    request: Request,
    order_id: int,
    paymentId: str,
    PayerID: str,
    db: Session = Depends(get_db)
):
    session_service = SessionService(request)
    paypal_service = PayPalService(db)
    
    try:
        # Get the order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Get the buyer
        buyer = db.query(User).filter(User.id == order.buyer_id).first()
        if not buyer:
            raise HTTPException(status_code=404, detail="Buyer not found")

        # Execute the payment
        success = paypal_service.execute_payment(paymentId, PayerID)
        
        if not success:
            raise HTTPException(status_code=400, detail="Payment execution failed")
        
        # Store user session data
        session_service.set_user_session(buyer.id, buyer.username)
        
        return RedirectResponse(url="/users/order-history", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payment/cancel/{order_id}")
async def payment_cancel(
    order_id: int, 
    db: Session = Depends(get_db)
):
    # Update order status to cancelled
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "cancelled"
        db.commit()
    
    return RedirectResponse(url="/users/order-history", status_code=303) 