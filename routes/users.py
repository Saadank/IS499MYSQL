from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import UserService
from services.session_service import SessionService
from dependencies import require_auth

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth)
):
    session_service = SessionService(request)
    user_service = UserService(db)
    
    user_data = user_service.get_user_profile_data(user_id)
    template_data = session_service.get_template_data(user_data)
    
    return templates.TemplateResponse("profile.html", template_data) 