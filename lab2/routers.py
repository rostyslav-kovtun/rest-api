from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from models import Book, BookCreate, library

router = APIRouter(prefix="/api/v1", tags=["books"])


async def find_book(book_id: str) -> Book:
    for book in library:
        if book.id == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Книгу з ID {book_id} не знайдено"
    )


@router.get("/books", response_model=Dict[str, Any])
async def get_all_books():
    return {
        "count": len(library),
        "books": [book.model_dump() for book in library]
    }


@router.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str):
    return await find_book(book_id)


@router.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate):
    new_book = Book(**book_data.model_dump())
    library.append(new_book)
    return new_book


@router.delete("/books/{book_id}")
async def delete_book(book_id: str):
    book = await find_book(book_id)
    library.remove(book)
    return {"message": f"Книгу '{book.title}' видалено"}