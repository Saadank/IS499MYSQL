from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from services.auction_service import AuctionService
from services.license_plate_service import LicensePlateService
from services.session_service import SessionService
from datetime import datetime
from utils.template_config import templates

router = APIRouter(prefix="/auctions", tags=["auctions"])

@router.get("/", response_class=HTMLResponse)
async def auction_page(request: Request, db: Session = Depends(get_db)):
    session_service = SessionService(request)
    auction_service = AuctionService(db)
    plate_service = LicensePlateService(db)
    
    active_auction = auction_service.get_active_auction()
    if active_auction:
        plate = plate_service.get_license_plate(active_auction.plate_id)
        time_left = (active_auction.end_time - datetime.utcnow()).total_seconds()
    else:
        plate = None
        time_left = 0
    
    auction_history = auction_service.get_auction_history()
    
    template_data = session_service.get_template_data({
        "active_auction": active_auction,
        "plate": plate,
        "time_left": time_left,
        "auction_history": auction_history,
        "user_id": request.session.get("user_id")
    })
    
    return templates.TemplateResponse("auction.html", template_data)

@router.post("/bid/{auction_id}")
async def place_bid(
    request: Request,
    auction_id: int,
    amount: float,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Please login to place a bid")
    
    auction_service = AuctionService(db)
    bid = auction_service.place_bid(auction_id, user_id, amount)
    
    if not bid:
        raise HTTPException(status_code=400, detail="Invalid bid")
    
    return RedirectResponse(url="/auctions", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/end/{auction_id}")
async def end_auction(
    request: Request,
    auction_id: int,
    db: Session = Depends(get_db)
):
    auction_service = AuctionService(db)
    auction = auction_service.end_auction(auction_id)
    
    if not auction:
        raise HTTPException(status_code=400, detail="Invalid auction")
    
    return RedirectResponse(url="/auctions", status_code=status.HTTP_303_SEE_OTHER) 