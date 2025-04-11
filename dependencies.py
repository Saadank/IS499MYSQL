from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from typing import Optional

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[int]:
    """Get the current user ID from the session. Returns None if not logged in."""
    user_id = request.session.get("user_id")
    if user_id:
        auth_service = AuthService(db)
        user = auth_service.get_user(user_id)
        if user:
            return user_id
    return None

async def require_auth(request: Request, db: Session = Depends(get_db)) -> int:
    """Require authentication. Redirects to login if not authenticated."""
    user_id = await get_current_user(request, db)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Not authenticated",
            headers={"Location": "/login"}
        )
    return user_id 