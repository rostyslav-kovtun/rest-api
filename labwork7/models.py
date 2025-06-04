from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional
from datetime import datetime

class Book(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str = Field(..., min_length=1, max_length=150)
    author: str = Field(..., min_length=1, max_length=100)
    year_published: int = Field(..., ge=1000, le=2025)
    genre: str = Field(..., min_length=1, max_length=50)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    author: str = Field(..., min_length=1, max_length=100)
    year_published: int = Field(..., ge=1000, le=2025)
    genre: str = Field(..., min_length=1, max_length=50)

class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: str}

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str