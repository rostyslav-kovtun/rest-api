from flask import Blueprint, jsonify, request, abort
from typing import Union, Dict, Any
from marshmallow import ValidationError

from .models import Book, library
from .schemas import BookSchema

book_routes = Blueprint("book_routes", __name__)
book_schema = BookSchema()


def format_response(data: Any, status_code: int = 200) -> tuple:
    return jsonify(data), status_code


def find_book(book_id: str) -> Union[Book, None]: # пошук за ID
    for book in library:
        if book.id == book_id:
            return book
    return None


@book_routes.route("/books", methods=["GET"]) # отримати всі книги
def get_all_books() -> tuple:
    books_data = [book.as_dict() for book in library]
    return format_response({"count": len(books_data), "books": books_data})


@book_routes.route("/books/<string:book_id>", methods=["GET"]) # отримати книги за ID
def get_book(book_id: str) -> tuple:
    book = find_book(book_id)
    if not book:
        return format_response({"error": f"Книгу з ID {book_id} не знайдено"}, 404)
    return format_response(book.as_dict())


@book_routes.route("/books", methods=["POST"]) # щоб створити якусь книгу
def create_book() -> tuple:
    try:
        request_data = request.get_json()
        if not request_data:
            return format_response({"error": "Не надано даних у форматі JSON"}, 400)
        
        # валідація
        book_data = book_schema.load(request_data)
        
        new_book = Book(**book_data)
        library.append(new_book)
        
        return format_response(new_book.as_dict(), 201)
    
    except ValidationError as e:
        return format_response({"validation_errors": e.messages}, 422)
    except Exception as e:
        return format_response({"server_error": str(e)}, 500)


@book_routes.route("/books/<string:book_id>", methods=["DELETE"]) # видалення якоїсь книги
def remove_book(book_id: str) -> tuple:
    book = find_book(book_id)
    if not book:
        return format_response({"error": f"Книгу з ID {book_id} не знайдено"}, 404)
    
    library.remove(book)
    return format_response({"message": f"Книгу '{book.title}' видалено"}, 200)