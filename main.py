from fastapi import FastAPI, Request, Depends, BackgroundTasks, Query, HTTPException
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
from typing import Optional

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
async def home(
    request: Request,
    digit1: Optional[str] = Query(None, min_length=0, max_length=1, regex="^[0-9x]?$"),
    digit2: Optional[str] = Query(None, min_length=0, max_length=1, regex="^[0-9x]?$"),
    digit3: Optional[str] = Query(None, min_length=0, max_length=1, regex="^[0-9x]?$"),
    digit4: Optional[str] = Query(None, min_length=0, max_length=1, regex="^[0-9x]?$"),
    letter1: Optional[str] = Query(None),
    letter2: Optional[str] = Query(None),
    letter3: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("newest", regex="^(newest|oldest|price_high|price_low)$"),
    db: Session = Depends(get_db)
):
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
    
    # Get plates with search criteria
    plates = plate_service.get_license_plates(
        digit1=digit1.strip() if digit1 and digit1.strip() else None,
        digit2=digit2.strip() if digit2 and digit2.strip() else None,
        digit3=digit3.strip() if digit3 and digit3.strip() else None,
        digit4=digit4.strip() if digit4 and digit4.strip() else None,
        letter1=cleaned_letters[0],
        letter2=cleaned_letters[1],
        letter3=cleaned_letters[2],
        sort_by=sort_by
    )
    
    # Use the standardized letter mapping from LicensePlateService
    letter_english = LicensePlateService.LETTER_ENGLISH
    letter_arabic = LicensePlateService.LETTER_ARABIC
    valid_letters = LicensePlateService.VALID_LETTERS
    
    template_data = session_service.get_template_data({
        "plates": plates,
        "letter_english": letter_english,
        "letter_arabic": letter_arabic,
        "valid_letters": valid_letters,
        "digit1": digit1,
        "digit2": digit2,
        "digit3": digit3,
        "digit4": digit4,
        "letter1": letter1,
        "letter2": letter2,
        "letter3": letter3,
        "sort_by": sort_by
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

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """About Us page"""
    session_service = SessionService(request)
    template_data = session_service.get_template_data({})
    return templates.TemplateResponse("about.html", template_data)

@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Terms & Conditions page"""
    session_service = SessionService(request)
    template_data = session_service.get_template_data({})
    return templates.TemplateResponse("terms.html", template_data)

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Privacy Policy page"""
    session_service = SessionService(request)
    template_data = session_service.get_template_data({})
    return templates.TemplateResponse("privacy.html", template_data) 