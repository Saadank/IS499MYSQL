from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from database import get_db
from services.payment_service import PaymentService
from services.session_service import SessionService
from utils.template_config import templates
from fastapi.responses import HTMLResponse, RedirectResponse
from models import Order, LicensePlate

router = APIRouter()

@router.get("/payment/{order_id}", response_class=HTMLResponse)
async def payment_page(request: Request, order_id: int, db: Session = Depends(get_db)):
    session_service = SessionService(request)
    payment_service = PaymentService(db)
    
    # Get order details
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get plate details
    plate = db.query(LicensePlate).filter(LicensePlate.plateID == order.plate_id).first()
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    
    template_data = session_service.get_template_data({
        "order": order,
        "plate": plate
    })
    
    return templates.TemplateResponse("payment.html", template_data)

@router.post("/process-payment/{order_id}")
async def process_payment(
    request: Request,
    order_id: int,
    card_number: str = Form(...),
    expiry_date: str = Form(...),
    cvv: str = Form(...),
    db: Session = Depends(get_db)
):
    payment_service = PaymentService(db)
    
    # Process the payment
    success = payment_service.process_payment(order_id, card_number, expiry_date, cvv)
    
    if not success:
        raise HTTPException(status_code=400, detail="Payment failed")
    
    return {"message": "Payment successful"} 