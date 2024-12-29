from typing import List
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

# Book Schemas

class BookCreateData(BaseModel):
    title: str
    author: str
    page_count: int

# Token Schemas
class TokenResponseData(BaseModel):
    id: int
    email: EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str  # Added refresh_token field
    token_type: str

class TokenRefreshRequest(BaseModel):  # Added schema for refresh request
    refresh_token: str

# User Schemas
class UserCreate(BaseModel):  # Renamed class to follow naming convention
    username: str
    email: EmailStr
    password: str
    ph_number: str
    role:str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    
class BookResponseData(BaseModel):
    id: int
    title: str
    author: str
    page_count: int
    created_at: datetime
    user: UserOut
    class Config:
        from_attributes=True

class EmailModel(BaseModel):
    addresses : List[EmailStr]


# Schemas for Password Reset
class PasswordResetRequestModel(BaseModel):
    email: EmailStr

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str