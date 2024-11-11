from datetime import datetime
from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    admin = "admin"
    editor = "editor"
    lector = "lector"


class LoginRequest(BaseModel):
    email: str
    password: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str
    

class UserBase(BaseModel):
    name_complete: str
    email: EmailStr
    role: str
    active: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class UserCreate(UserBase):
    password: str
    
class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: Optional[str]     

    class Config:
        orm_mode = True