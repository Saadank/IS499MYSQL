from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from dependencies import require_auth
from services.wishlist_service import WishlistService
from utils.template_config import templates
from services.license_plate_service import LicensePlateService

router = APIRouter(prefix="", tags=["wishlist"])

@router.get("/wishlist", response_class=HTMLResponse)
async def wishlist_page(
    request: Request,
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db)
):
    wishlist_service = WishlistService(db)
    wishlist_plates = wishlist_service.get_wishlist(user_id)
    
    # Use the standardized letter mapping from LicensePlateService
    letter_english = LicensePlateService.LETTER_ENGLISH
    
    return templates.TemplateResponse("wishlist.html", {
        "request": request,
        "plates": wishlist_plates,
        "username": request.session.get("username"),
        "letter_english": letter_english
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