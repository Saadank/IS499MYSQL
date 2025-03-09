from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/profile", response_class=HTMLResponse)
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