from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from .schemas import UserLogin, UserSignup

router = APIRouter(prefix="", tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate input using schema
    login_data = UserLogin(username=username, password=password)
    
    auth_service = AuthService(db)
    user = auth_service.verify_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Set session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    idnumber: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate input using schema
    signup_data = UserSignup(
        username=username,
        email=email,
        password=password,
        confirm_password=confirm_password,
        firstname=firstname,
        lastname=lastname,
        idnumber=idnumber,
        address=address
    )
    
    if signup_data.password != signup_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    auth_service = AuthService(db)
    if auth_service.get_user_by_username(signup_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if auth_service.get_user_by_email(signup_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = auth_service.create_user(
        username=signup_data.username,
        email=signup_data.email,
        password=signup_data.password,
        firstname=signup_data.firstname,
        lastname=signup_data.lastname,
        idnumber=signup_data.idnumber,
        address=signup_data.address
    )
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER) 