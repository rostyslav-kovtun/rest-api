from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

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


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year_published: Optional[int] = Field(None, ge=1000, le=2025)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)


class BookInDB(Book):
    pass