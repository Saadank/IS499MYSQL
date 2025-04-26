from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from routes import auth, listings, users, wishlist, api, payment
from routes.admin_routes import router as admin_router
from routes import auth, listings, users, wishlist, api, support
from starlette.middleware.sessions import SessionMiddleware
from services.license_plate_service import LicensePlateService
from services.session_service import SessionService
from datetime import datetime, timedelta
from utils.template_config import templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="License Plate Trading")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="Ssaadd1424",
    session_cookie="session_cookie"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create database tables
Base.metadata.create_all(bind=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(users.router)
app.include_router(wishlist.router)
app.include_router(api.router)
app.include_router(payment.router)
app.include_router(support.router)
app.include_router(admin_router)

@app.get("/", response_class=HTMLResponse, name="home_page")
async def home(request: Request, db: Session = Depends(get_db)):
    session_service = SessionService(request)
    plate_service = LicensePlateService(db)
    plates = plate_service.get_license_plates()
    
    # Use the standardized letter mapping from LicensePlateService
    letter_english = LicensePlateService.LETTER_ENGLISH
    letter_arabic = LicensePlateService.LETTER_ARABIC
    valid_letters = LicensePlateService.VALID_LETTERS
    
    template_data = session_service.get_template_data({
        "plates": plates,
        "letter_english": letter_english,
        "letter_arabic": letter_arabic,
        "valid_letters": valid_letters
    })
    
    return templates.TemplateResponse("landingpage.html", template_data)

@app.get("/api/", response_model=dict)
def api_root():
    return {"message": "Welcome to the License Plate Marketplace API"}

@app.get("/auctions", response_class=HTMLResponse)
async def auctions_page(request: Request):
    """Auction feature coming soon page"""
    session_service = SessionService(request)
    template_data = session_service.get_template_data({})
    return templates.TemplateResponse("auction.html", template_data) 