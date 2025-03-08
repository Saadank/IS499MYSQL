from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from typing import Optional
from pydantic import BaseModel
import hashlib

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)

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
async def home(request: Request):
    return templates.TemplateResponse("landingpage.html", {"request": request})

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
    # Here you would verify the user credentials against the database
    # For now, we'll redirect to home page
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
    
    # Here you would create a new user in the database
    # For now, we'll redirect to login page
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
    # Here you would save the listing to the database
    # and handle the image upload
    # For now, we'll redirect to home page
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/auction", response_class=HTMLResponse)
async def auction_page(request: Request):
    return templates.TemplateResponse("auction.html", {"request": request})

@app.get("/forsale", response_class=HTMLResponse)
async def forsale_page(request: Request):
    return templates.TemplateResponse("forsale.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request}) 