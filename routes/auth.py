from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from services.session_service import SessionService
from .schemas import UserLogin, UserSignup
from utils.template_config import templates

router = APIRouter(prefix="", tags=["auth"])

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    session_service = SessionService(request)
    return templates.TemplateResponse("login.html", session_service.get_template_data())

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    session_service = SessionService(request)
    
    user = await auth_service.login_user(username, password)
    session_service.set_user_session(user.id, user.username)
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    session_service = SessionService(request)
    return templates.TemplateResponse("signup.html", session_service.get_template_data())

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

@router.get("/logout")
async def logout(request: Request):
    session_service = SessionService(request)
    session_service.clear_session()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER) 