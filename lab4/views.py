from flask import Blueprint, jsonify, request, abort
from typing import Dict, Any, Optional
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, asc
import base64
import json

from models import Book, db
from schemas import BookSchema, CursorPaginationSchema

book_routes = Blueprint("book_routes", __name__)
book_schema = BookSchema()
cursor_pagination_schema = CursorPaginationSchema()


def format_response(data: Any, status_code: int = 200) -> tuple:
    return jsonify(data), status_code


def encode_cursor(book_id: str, created_at: str) -> str:
    cursor_data = {
        'id': book_id,
        'created_at': created_at
    }
    cursor_json = json.dumps(cursor_data)
    return base64.b64encode(cursor_json.encode()).decode()


def decode_cursor(cursor: str) -> Dict[str, str]:
    try:
        cursor_json = base64.b64decode(cursor.encode()).decode()
        return json.loads(cursor_json)
    except (ValueError, json.JSONDecodeError):
        raise ValueError("Невірний формат курсора")


def get_books_with_cursor(cursor: Optional[str] = None, limit: int = 10, order: str = 'asc') -> Dict[str, Any]:

    query = Book.query

    if cursor:
        try:
            cursor_data = decode_cursor(cursor)
            cursor_id = cursor_data['id']
            cursor_created_at = cursor_data['created_at']
            
            if order == 'asc':
                query = query.filter(
                    (Book.created_at > cursor_created_at) |
                    ((Book.created_at == cursor_created_at) & (Book.id > cursor_id))
                )
                query = query.order_by(asc(Book.created_at), asc(Book.id))
            else:
                query = query.filter(
                    (Book.created_at < cursor_created_at) |
                    ((Book.created_at == cursor_created_at) & (Book.id < cursor_id))
                )
                query = query.order_by(desc(Book.created_at), desc(Book.id))
        except ValueError as e:
            raise ValueError(f"Помилка курсора: {str(e)}")
    else:
        if order == 'asc':
            query = query.order_by(asc(Book.created_at), asc(Book.id))
        else:
            query = query.order_by(desc(Book.created_at), desc(Book.id))
    
    books = query.limit(limit + 1).all()

    has_next = len(books) > limit
    if has_next:
        books = books[:limit]
    
    next_cursor = None
    prev_cursor = None
    
    if books:
        if has_next:
            last_book = books[-1]
            next_cursor = encode_cursor(
                last_book.id, 
                last_book.created_at.isoformat()
            )
        
        if cursor:
            first_book = books[0]
            prev_cursor = encode_cursor(
                first_book.id,
                first_book.created_at.isoformat()
            )
    
    return {
        'books': [book.as_dict() for book in books],
        'pagination': {
            'has_next': has_next,
            'has_prev': cursor is not None,
            'next_cursor': next_cursor,
            'prev_cursor': prev_cursor,
            'limit': limit,
            'count': len(books)
        }
    }


@book_routes.route("/books", methods=["GET"])
def get_all_books() -> tuple:
    try:
        pagination_data = cursor_pagination_schema.load(request.args)
        cursor = pagination_data.get('cursor')
        limit = pagination_data.get('limit', 10)
        order = pagination_data.get('order', 'asc')

        result = get_books_with_cursor(cursor, limit, order)
        
        return format_response(result)
        
    except ValidationError as e:
        return format_response({"validation_errors": e.messages}, 422)
    except ValueError as e:
        return format_response({"cursor_error": str(e)}, 400)
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