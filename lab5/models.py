from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional
from datetime import datetime


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    author: str = Field(..., min_length=1, max_length=100)
    year_published: int = Field(..., ge=1000, le=2025)
    genre: str = Field(..., min_length=1, max_length=50)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year_published: Optional[int] = Field(None, ge=1000, le=2025)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)


class Book(BookBase):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            PydanticObjectId: str
        }


class BookResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    author: str
    year_published: int
    genre: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True