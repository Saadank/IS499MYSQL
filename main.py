from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from routes import auth, listings, users
from starlette.middleware.sessions import SessionMiddleware
from services.license_plate_service import LicensePlateService

app = FastAPI(title="License Plate Trading")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="Ssaadd1424",
    session_cookie="session_cookie"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(users.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    plate_service = LicensePlateService(db)
    plates = plate_service.get_license_plates()
    
    return templates.TemplateResponse("landingpage.html", {
        "request": request,
        "plates": plates,
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username")
    }) 