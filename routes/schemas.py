from pydantic import BaseModel, EmailStr, constr, confloat
from typing import Optional
from pydantic import validator
import re

class UserLogin(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)

class UserSignup(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: str
    password: constr(min_length=6)
    confirm_password: str
    firstname: constr(min_length=1, max_length=50)
    lastname: constr(min_length=1, max_length=50)
    idnumber: constr(min_length=10, max_length=10, pattern=r'^\d{10}$')
    address: constr(min_length=1, max_length=200)
    phone_number: constr(min_length=10, max_length=10, pattern=r'^\d{10}$')
    iban: Optional[constr(min_length=1, max_length=34)] = None

    @validator('email')
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Please enter a valid email address')
        return v.lower()  # Convert email to lowercase

class LicensePlateCreate(BaseModel):
    plateNumber: constr(min_length=1, max_length=10)
    plateLetter: constr(min_length=1, max_length=10)
    description: str | None = None
    price: confloat(gt=0)
    image_path: Optional[str] = None

class LicensePlateUpdate(BaseModel):
    plateNumber: constr(min_length=1, max_length=10) | None = None
    plateLetter: constr(min_length=1, max_length=10) | None = None
    description: str | None = None
    price: confloat(gt=0) | None = None
    image_path: Optional[str] = None 