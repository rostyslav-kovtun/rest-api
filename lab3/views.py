from flask import Blueprint, jsonify, request, abort
from typing import Union, Dict, Any
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from .models import Book, db
from .schemas import BookSchema, PaginationSchema

book_routes = Blueprint("book_routes", __name__)
book_schema = BookSchema()
pagination_schema = PaginationSchema()


def format_response(data: Any, status_code: int = 200) -> tuple:
    return jsonify(data), status_code


@book_routes.route("/books", methods=["GET"])
def get_all_books() -> tuple:
    try:
        pagination_data = pagination_schema.load(request.args)
        page = pagination_data.get('page', 1)
        per_page = pagination_data.get('per_page', 10)
        
        books_paginated = Book.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        books_data = [book.as_dict() for book in books_paginated.items]
        
        response_data = {
            "books": books_data,
            "pagination": {
                "page": books_paginated.page,
                "per_page": books_paginated.per_page,
                "total": books_paginated.total,
                "pages": books_paginated.pages,
                "has_next": books_paginated.has_next,
                "has_prev": books_paginated.has_prev,
                "next_page": books_paginated.next_num if books_paginated.has_next else None,
                "prev_page": books_paginated.prev_num if books_paginated.has_prev else None
            }
        }
        
        return format_response(response_data)
        
    except ValidationError as e:
        return format_response({"validation_errors": e.messages}, 422)
    except SQLAlchemyError as e:
        return format_response({"database_error": str(e)}, 500)


@book_routes.route("/books/<string:book_id>", methods=["GET"])
def get_book(book_id: str) -> tuple:
    try:
        book = Book.query.get(book_id)
        if not book:
            return format_response({"error": f"Книгу з ID {book_id} не знайдено"}, 404)
        return format_response(book.as_dict())
    except SQLAlchemyError as e:
        return format_response({"database_error": str(e)}, 500)


@book_routes.route("/books", methods=["POST"])
def create_book() -> tuple:
    try:
        request_data = request.get_json()
        if not request_data:
            return format_response({"error": "Не надано даних у форматі JSON"}, 400)
        
        book_data = book_schema.load(request_data)
        
        new_book = Book(**book_data)
        db.session.add(new_book)
        db.session.commit()
        
        return format_response(new_book.as_dict(), 201)
    
    except ValidationError as e:
        db.session.rollback()
        return format_response({"validation_errors": e.messages}, 422)
    except SQLAlchemyError as e:
        db.session.rollback()
        return format_response({"database_error": str(e)}, 500)


@book_routes.route("/books/<string:book_id>", methods=["DELETE"])
def remove_book(book_id: str) -> tuple:
    try:
        book = Book.query.get(book_id)
        if not book:
            return format_response({"error": f"Книгу з ID {book_id} не знайдено"}, 404)
        
        book_title = book.title
        db.session.delete(book)
        db.session.commit()
        
        return format_response({"message": f"Книгу '{book_title}' видалено"}, 200)
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return format_response({"database_error": str(e)}, 500)