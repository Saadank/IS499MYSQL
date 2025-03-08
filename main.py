from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from typing import Optional
import crud, models
from pydantic import BaseModel
import hashlib
import os
from datetime import datetime

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic models for request validation
class UserLogin(BaseModel):
    username: str
    password: str

class UserSignup(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

class Listing(BaseModel):
    plate_number: str
    description: str
    price: float
    listing_type: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    listings = crud.get_listings(db)
    return templates.TemplateResponse("landingpage.html", {
        "request": request,
        "listings": listings
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.verify_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if crud.get_user_by_username(db, username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if crud.get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = crud.create_user(db, username, email, password)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/addlisting", response_class=HTMLResponse)
async def add_listing_page(request: Request):
    return templates.TemplateResponse("addlisting.html", {"request": request})

@app.post("/addlisting")
async def create_listing(
    request: Request,
    plate_number: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    listing_type: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Handle image upload
    image_path = None
    if image:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{image.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        image_path = f"uploads/{filename}"
    
    # For now, we'll use a hardcoded user_id (you should get this from the session)
    user_id = 1
    
    listing = crud.create_listing(
        db,
        plate_number=plate_number,
        description=description,
        price=price,
        listing_type=listing_type,
        owner_id=user_id,
        image_path=image_path
    )
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/auction", response_class=HTMLResponse)
async def auction_page(request: Request, db: Session = Depends(get_db)):
    listings = crud.get_listings_by_type(db, "auction")
    return templates.TemplateResponse("auction.html", {
        "request": request,
        "listings": listings
    })

@app.get("/forsale", response_class=HTMLResponse)
async def forsale_page(request: Request, db: Session = Depends(get_db)):
    listings = crud.get_listings_by_type(db, "sale")
    return templates.TemplateResponse("forsale.html", {
        "request": request,
        "listings": listings
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    # For now, we'll use a hardcoded user_id (you should get this from the session)
    user_id = 1
    user = crud.get_user(db, user_id)
    listings = crud.get_user_listings(db, user_id)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "listings": listings
    }) 