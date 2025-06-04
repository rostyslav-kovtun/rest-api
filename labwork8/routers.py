from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Dict, Any, Optional
from models import Book, BookCreate, User
from repository import book_repository
from auth import get_current_active_user, get_current_user_optional
from rate_limiter import rate_limiter

router = APIRouter(prefix="/api/v1", tags=["books"])

@router.get("/books/public", response_model=Dict[str, Any])
async def get_all_books_public(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):

    user_id = current_user.id if current_user else None
    await rate_limiter.check_rate_limit(request, user_id)
    
    books = await book_repository.get_all_books()
    response = {
        "count": len(books),
        "books": [book.model_dump() for book in books]
    }
    
    if current_user:
        response["user"] = current_user.username
        response["user_type"] = "authenticated"
    else:
        response["user_type"] = "anonymous"
    
    return response

@router.get("/books", response_model=Dict[str, Any])
async def get_all_books(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):

    await rate_limiter.check_rate_limit(request, current_user.id)
    
    books = await book_repository.get_all_books()
    return {
        "count": len(books),
        "books": [book.model_dump() for book in books],
        "user": current_user.username
    }

@router.get("/books/{book_id}", response_model=Book)
async def get_book(
    book_id: str, 
    request: Request,
    current_user: User = Depends(get_current_active_user)
):

    await rate_limiter.check_rate_limit(request, current_user.id)
    
    book = await book_repository.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено"
        )
    return book

@router.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate, 
    request: Request,
    current_user: User = Depends(get_current_active_user)
):

    await rate_limiter.check_rate_limit(request, current_user.id)
    
    return await book_repository.create_book(book_data)

@router.delete("/books/{book_id}")
async def delete_book(
    book_id: str, 
    request: Request,
    current_user: User = Depends(get_current_active_user)
):

    await rate_limiter.check_rate_limit(request, current_user.id)
    
    book = await book_repository.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено"
        )
    
    deleted = await book_repository.delete_book(book_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Помилка при видаленні"
        )
    
    return {
        "message": f"Книгу '{book.title}' видалено користувачем {current_user.username}"
    }