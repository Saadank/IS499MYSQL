from pydantic import BaseModel, EmailStr, constr, confloat

class UserLogin(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)

class UserSignup(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6)
    confirm_password: str

class LicensePlateCreate(BaseModel):
    plateNumber: constr(min_length=1, max_length=10)
    plateLetter: constr(min_length=1, max_length=10)
    description: str | None = None
    price: confloat(gt=0)

class LicensePlateUpdate(BaseModel):
    plateNumber: constr(min_length=1, max_length=10) | None = None
    plateLetter: constr(min_length=1, max_length=10) | None = None
    description: str | None = None
    price: confloat(gt=0) | None = None 