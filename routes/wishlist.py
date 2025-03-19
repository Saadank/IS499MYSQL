from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from dependencies import require_auth
from services.wishlist_service import WishlistService

router = APIRouter(prefix="", tags=["wishlist"])
templates = Jinja2Templates(directory="templates")

@router.get("/wishlist", response_class=HTMLResponse)
async def wishlist_page(
    request: Request,
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db)
):
    wishlist_service = WishlistService(db)
    wishlist_plates = wishlist_service.get_wishlist(user_id)
    
    return templates.TemplateResponse("wishlist.html", {
        "request": request,
        "plates": wishlist_plates,
        "username": request.session.get("username")
    })

@router.post("/wishlist/add/{plate_id}")
async def add_to_wishlist(
    plate_id: int,
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db)
):
    wishlist_service = WishlistService(db)
    if wishlist_service.add_to_wishlist(user_id, plate_id):
        return {"message": "Added to wishlist successfully"}
    raise HTTPException(status_code=400, detail="Failed to add to wishlist")

@router.post("/wishlist/remove/{plate_id}")
async def remove_from_wishlist(
    plate_id: int,
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db)
):
    wishlist_service = WishlistService(db)
    if wishlist_service.remove_from_wishlist(user_id, plate_id):
        return {"message": "Removed from wishlist successfully"}
    raise HTTPException(status_code=400, detail="Failed to remove from wishlist") 