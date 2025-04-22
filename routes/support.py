from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from services.session_service import SessionService
from utils.template_config import templates
from typing import Optional
from fastapi import HTTPException
import re

router = APIRouter(tags=["support"])

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

@router.get("/support", response_class=HTMLResponse)
async def support_page(request: Request, db: Session = Depends(get_db)):
    session_service = SessionService(request)
    template_data = session_service.get_template_data({})
    return templates.TemplateResponse("support.html", template_data)

@router.post("/support")
async def submit_support(
    request: Request,
    issue_type: str = Form(...),
    message: str = Form(...),
    email: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    session_service = SessionService(request)
    username = request.session.get("username")
    
    if not username and (not email or not is_valid_email(email)):
        raise HTTPException(status_code=400, detail="Please provide a valid email address")
    
    # TODO: Send email to support
    # For now, just redirect back with success message
    request.session["support_message"] = "Your message has been sent to our support team. We'll get back to you soon."
    
    return RedirectResponse(url="/support", status_code=303) 