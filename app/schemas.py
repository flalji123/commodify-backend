
from pydantic import BaseModel, EmailStr
from typing import Optional
class RegisterIn(BaseModel): email: EmailStr; password: str
class LoginIn(BaseModel): email: EmailStr; password: str
class TokenOut(BaseModel): access_token: str; token_type: str="bearer"
class CompanyIn(BaseModel): name: str; country: Optional[str]=""; notes: Optional[str]=""
class CompanyOut(CompanyIn): id:int; class Config: from_attributes=True
class TaskIn(BaseModel): title:str; status: Optional[str]="todo"
class TaskOut(TaskIn): id:int; class Config: from_attributes=True
class DDIn(BaseModel): name:str; country: Optional[str]=""
