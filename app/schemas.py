# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# -------- Auth --------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------- Companies (CRM) --------
class CompanyIn(BaseModel):
    name: str
    country: Optional[str] = ""
    notes: Optional[str] = ""

class CompanyOut(CompanyIn):
    id: int
    # Pydantic v2 config:
    model_config = {"from_attributes": True}


# -------- Tasks / Projects --------
class TaskIn(BaseModel):
    # make optional so updates can omit title
    title: Optional[str] = None
    status: Optional[str] = "todo"

class TaskOut(TaskIn):
    id: int
    model_config = {"from_attributes": True}


# -------- Due Diligence --------
class DDIn(BaseModel):
    name: str
    country: Optional[str] = ""
