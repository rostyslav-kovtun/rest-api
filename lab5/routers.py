from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any
from models import BookCreate, BookUpdate, BookResponse
import crud

router = APIRouter(prefix="/api/v1", tags=["books"])


@router.get("/books", response_model=Dict[str, Any])
async def get_all_books(
    skip: int = Query(0, ge=0, description="Кількість записів для пропуску"),
    limit: int = Query(10, ge=1, le=100, description="Максимальна кількість записів")
):
    try:
        books = await crud.get_all_books(skip=skip, limit=limit)
        total_count = await crud.get_books_count()

        books_data = []
        for book in books:
            book_dict = book.model_dump()
            book_dict["id"] = str(book_dict["_id"])
            books_data.append(book_dict)
        
        return {
            "books": books_data,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_count,
                "count": len(books_data)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка отримання книг: {str(e)}"
        )


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str):
    book = await crud.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено"
        )

    book_dict = book.model_dump()
    book_dict["id"] = str(book_dict["_id"])
    return BookResponse(**book_dict)


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate):
    try:
        new_book = await crud.create_book(book_data)

        book_dict = new_book.model_dump()
        book_dict["id"] = str(book_dict["_id"])
        return BookResponse(**book_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка створення книги: {str(e)}"
        )


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: str, book_data: BookUpdate):

    existing_book = await crud.get_book_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено"
        )
    
    try:
        updated_book = await crud.update_book(book_id, book_data)
        if not updated_book:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Помилка оновлення книги"
            )

        book_dict = updated_book.model_dump()
        book_dict["id"] = str(book_dict["_id"])
        return BookResponse(**book_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка оновлення книги: {str(e)}"
        )


@router.delete("/books/{book_id}")
async def delete_book(book_id: str):
    existing_book = await crud.get_book_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено"
        )
    
    try:
        success = await crud.delete_book(book_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Помилка видалення книги"
            )
        
        return {"message": f"Книгу '{existing_book.title}' видалено"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка видалення книги: {str(e)}"
        )