from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from services.session_service import SessionService
from .schemas import UserLogin, UserSignup
from utils.template_config import templates
from models import User

router = APIRouter(prefix="", tags=["auth"])

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session_service = SessionService(request)
    user_id = session_service.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    session_service = SessionService(request)
    template_data = session_service.get_template_data({"error": error})
    return templates.TemplateResponse("login.html", template_data)

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    session_service = SessionService(request)
    
    try:
        # Validate input using schema
        login_data = UserLogin(username=username, password=password)
        user = await auth_service.login_user(username, password)
        session_service.set_user_session(user.id, user.username)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        error_message = str(e)
        if "Your account has been banned" in error_message:
            return RedirectResponse(url="/login?error=Your account has been banned", status_code=status.HTTP_303_SEE_OTHER)
        # Show generic error message for all other validation and authentication errors
        return RedirectResponse(url="/login?error=Incorrect username or password", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(
    request: Request, 
    error: str = None,
    username: str = None,
    email: str = None,
    firstname: str = None,
    lastname: str = None,
    idnumber: str = None,
    address: str = None
):
    session_service = SessionService(request)
    template_data = session_service.get_template_data({
        "error": error,
        "username": username,
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "idnumber": idnumber,
        "address": address
    })
    return templates.TemplateResponse("signup.html", template_data)

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
    auth_service = AuthService(db)
    try:
        await auth_service.register_user(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            firstname=firstname,
            lastname=lastname,
            idnumber=idnumber,
            address=address
        )
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        error_message = str(e)
        if "string_too_short" in error_message:
            if "username" in error_message:
                error_message = "Username must be at least 3 characters long"
            elif "password" in error_message:
                error_message = "Password must be at least 6 characters long"
        elif "email" in error_message.lower():
            error_message = "Please enter a valid email address"
        elif "Username already registered" in error_message:
            error_message = "This username is already taken"
        elif "Email already registered" in error_message:
            error_message = "This email is already registered"
        elif "ID number already registered" in error_message:
            error_message = "This ID number is already registered"
        elif "This ID number is banned from registration" in error_message:
            error_message = "This ID number is banned from registration"
        elif "Passwords do not match" in error_message:
            error_message = "Passwords do not match"
        else:
            error_message = "An error occurred during registration. Please try again."
        
        # Preserve form data
        form_data = {
            "error": error_message,
            "username": username,
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "idnumber": idnumber,
            "address": address
        }
        
        return RedirectResponse(
            url=f"/signup?error={error_message}&username={username}&email={email}&firstname={firstname}&lastname={lastname}&idnumber={idnumber}&address={address}", 
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.get("/logout")
async def logout(request: Request):
    session_service = SessionService(request)
    session_service.clear_session()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER) 