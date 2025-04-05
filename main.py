from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from routes import auth, listings, users, auctions, wishlist
from starlette.middleware.sessions import SessionMiddleware
from services.license_plate_service import LicensePlateService
from services.auction_service import AuctionService
from services.session_service import SessionService
import asyncio
from datetime import datetime, timedelta

app = FastAPI(title="License Plate Trading")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="Ssaadd1424",
    session_cookie="session_cookie"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(users.router)
app.include_router(auctions.router)
app.include_router(wishlist.router)

async def create_new_auction(db: Session):
    while True:
        try:
            auction_service = AuctionService(db)
            plate_service = LicensePlateService(db)
            
            # Check if there's an active auction
            active_auction = auction_service.get_active_auction()
            if not active_auction:
                # Get a random plate that's not currently in auction
                available_plates = plate_service.get_available_plates()
                if available_plates:
                    plate = available_plates[0]  # Get the first available plate
                    start_price = plate.price * 0.8  # Start at 80% of the original price
                    auction_service.create_new_auction(plate.plateID, start_price)
            
            # Wait for 5 minutes before checking again
            await asyncio.sleep(300)  # 300 seconds = 5 minutes
            
        except Exception as e:
            print(f"Error in auction creation task: {e}")
            await asyncio.sleep(60)  # Wait a minute before retrying

@app.on_event("startup")
async def startup_event():
    # Start the background task for creating new auctions
    asyncio.create_task(create_new_auction(next(get_db())))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    session_service = SessionService(request)
    plate_service = LicensePlateService(db)
    plates = plate_service.get_license_plates()
    
    template_data = session_service.get_template_data({
        "plates": plates
    })
    
    return templates.TemplateResponse("landingpage.html", template_data) 