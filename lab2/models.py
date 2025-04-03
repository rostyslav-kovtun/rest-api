from pydantic import BaseModel, Field
import uuid
from typing import List


class Book(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=150)
    author: str = Field(..., min_length=1, max_length=100)
    year_published: int = Field(..., ge=1000, le=2025)
    genre: str = Field(..., min_length=1, max_length=50)

    class Config:
        from_attributes = True


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    author: str = Field(..., min_length=1, max_length=100)
    year_published: int = Field(..., ge=1000, le=2025)
    genre: str = Field(..., min_length=1, max_length=50)


library: List[Book] = [
    Book(
        title="Kobzar",
        author="Taras Shevchenko",
        year_published=1840,
        genre="poetry"
    ),
    Book(
        title="1984",
        author="George Orwell",
        year_published=1949,
        genre="dystopian"
    ),
    Book(
        title="Norwegian Wood",
        author="Haruki Murakami",
        year_published=1987,
        genre="fiction"
    )
]