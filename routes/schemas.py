from pydantic import BaseModel, EmailStr, constr, confloat
from typing import Optional

class UserLogin(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)

class UserSignup(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6)
    confirm_password: str
    firstname: constr(min_length=1, max_length=50)
    lastname: constr(min_length=1, max_length=50)
    idnumber: constr(min_length=1, max_length=20)
    address: constr(min_length=1, max_length=200)
    phone_number: constr(min_length=10, max_length=10, pattern=r'^\d{10}$')
    iban: Optional[constr(min_length=1, max_length=34)] = None

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