from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str
    idnumber: str
    address: str
    phone_number: Optional[str] = None
    iban: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    idnumber: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    iban: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    firstname: str
    lastname: str
    idnumber: str
    address: str
    phone_number: Optional[str] = None
    iban: Optional[str] = None
    created_at: datetime
    is_admin: bool = False
    is_banned: bool = False

    class Config:
        from_attributes = True

class LicensePlateResponse(BaseModel):
    plateID: int
    plateNumber: str
    plateLetter: str
    description: Optional[str]
    price: float
    owner_id: int
    image_path: Optional[str]
    created_at: datetime
    listing_type: str
    buy_now_price: Optional[float]
    city: Optional[str]
    transfer_cost: Optional[str]
    plate_type: Optional[str]

    class Config:
        from_attributes = True 