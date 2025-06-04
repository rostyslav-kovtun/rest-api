from flask import Blueprint, jsonify, request, url_for
from typing import Dict, Any
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from models import Book, db
from schemas import BookSchema
from config import Config

book_routes = Blueprint("book_routes", __name__)
book_schema = BookSchema()


def format_response(data: Any, status_code: int = 200) -> tuple:
    return jsonify(data), status_code


def get_pagination_params() -> tuple:

    try:
        limit = int(request.args.get('limit', Config.DEFAULT_PAGE_SIZE))
        offset = int(request.args.get('offset', 0))

        if limit > Config.MAX_PAGE_SIZE:
            limit = Config.MAX_PAGE_SIZE
        elif limit < 1:
            limit = Config.DEFAULT_PAGE_SIZE
            
        if offset < 0:
            offset = 0
            
        return limit, offset
    except (ValueError, TypeError):
        return Config.DEFAULT_PAGE_SIZE, 0


def create_pagination_links(limit: int, offset: int, total_count: int) -> Dict[str, str]:

    links = {}

    current_page = (offset // limit) + 1
    total_pages = (total_count + limit - 1) // limit
    
    base_url = request.base_url

    if current_page > 1:
        links['first'] = f"{base_url}?limit={limit}&offset=0"
        links['prev'] = f"{base_url}?limit={limit}&offset={max(0, offset - limit)}"

    if current_page < total_pages:
        next_offset = offset + limit
        last_offset = (total_pages - 1) * limit
        links['next'] = f"{base_url}?limit={limit}&offset={next_offset}"
        links['last'] = f"{base_url}?limit={limit}&offset={last_offset}"
    
    return links


@book_routes.route("/books", methods=["GET"])
def get_all_books() -> tuple:

    try:
        limit, offset = get_pagination_params()

        query = Book.query.offset(offset).limit(limit)
        books = query.all()
        
        total_count = Book.query.count()

        books_data = [book.as_dict() for book in books]

        links = create_pagination_links(limit, offset, total_count)
        
        response_data = {
            "books": books_data,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "count": len(books_data)
            },
            "links": links
        }
        
        return format_response(response_data)
        
    except SQLAlchemyError as e:
        return format_response({"database_error": str(e)}, 500)
    except Exception as e:
        return format_response({"server_error": str(e)}, 500)


@book_routes.route("/books/<string:book_id>", methods=["GET"])
def get_book(book_id: str) -> tuple:
    try:
        book = Book.query.get(book_id)
        if not book:
            return format_response({"error": f"Книгу з ID {book_id} не знайдено"}, 404)
        
        return format_response(book.as_dict())
        
    except SQLAlchemyError as e:
        return format_response({"database_error": str(e)}, 500)
    except Exception as e:
        return format_response({"server_error": str(e)}, 500)


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
        return format_response({"validation_errors": e.messages}, 422)
    except SQLAlchemyError as e:
        db.session.rollback()
        return format_response({"database_error": str(e)}, 500)
    except Exception as e:
        db.session.rollback()
        return format_response({"server_error": str(e)}, 500)


@book_routes.route("/books/<string:book_id>", methods=["PUT"])
def update_book(book_id: str) -> tuple:
    try:
        book = Book.query.get(book_id)
        if not book:
            return format_response({"error": f"Книгу з ID {book_id} не знайдено"}, 404)
        
        request_data = request.get_json()
        if not request_data:
            return format_response({"error": "Не надано даних у форматі JSON"}, 400)

        book_data = book_schema.load(request_data)
        
        for field, value in book_data.items():
            setattr(book, field, value)
        
        db.session.commit()
        
        return format_response(book.as_dict())
    
    except ValidationError as e:
        return format_response({"validation_errors": e.messages}, 422)
    except SQLAlchemyError as e:
        db.session.rollback()
        return format_response({"database_error": str(e)}, 500)
    except Exception as e:
        db.session.rollback()
        return format_response({"server_error": str(e)}, 500)


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
    except Exception as e:
        db.session.rollback()
        return format_response({"server_error": str(e)}, 500)