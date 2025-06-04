from flask import Blueprint, jsonify, request, url_for
from typing import Dict, Any, Optional, List
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from datetime import datetime

from models import Book, db
from schemas import BookSchema
from config import Config

book_routes = Blueprint("book_routes", __name__)
book_schema = BookSchema()


def format_response(data: Any, status_code: int = 200) -> tuple:
    return jsonify(data), status_code


def get_cursor_pagination_params() -> tuple:
    try:
        limit = int(request.args.get('limit', Config.DEFAULT_PAGE_SIZE))
        cursor = request.args.get('cursor', None)

        if limit > Config.MAX_PAGE_SIZE:
            limit = Config.MAX_PAGE_SIZE
        elif limit < 1:
            limit = Config.DEFAULT_PAGE_SIZE
            
        return limit, cursor
    except (ValueError, TypeError):
        return Config.DEFAULT_PAGE_SIZE, None


def build_cursor_query(cursor: Optional[str], limit: int) -> tuple:
    base_query = Book.query.order_by(Book.created_at.desc(), Book.id.desc())
    
    if cursor:
        created_at, book_id = Book.parse_cursor(cursor)
        
        if created_at:
            base_query = base_query.filter(
                or_(
                    Book.created_at < created_at,
                    and_(
                        Book.created_at == created_at,
                        Book.id < book_id
                    )
                )
            )
        else:
            base_query = base_query.filter(Book.id < book_id)

    books = base_query.limit(limit + 1).all()
    
    has_next = len(books) > limit
    if has_next:
        books = books[:limit]
    
    return books, has_next


def create_cursor_links(books: List[Book], has_next: bool, limit: int) -> Dict[str, str]:
    """Створює лінки для cursor пагінації"""
    links = {}
    base_url = request.base_url
    
    if books:

        if has_next:
            next_cursor = books[-1].get_cursor()
            links['next'] = f"{base_url}?limit={limit}&cursor={next_cursor}"

        links['first'] = f"{base_url}?limit={limit}"
    
    return links


@book_routes.route("/books", methods=["GET"])
def get_all_books() -> tuple:
    try:
        limit, cursor = get_cursor_pagination_params()

        books, has_next = build_cursor_query(cursor, limit)

        books_data = [book.as_dict() for book in books]

        links = create_cursor_links(books, has_next, limit)
        
        pagination_info = {
            "limit": limit,
            "count": len(books_data),
            "has_next": has_next,
            "cursor": cursor
        }
        
        if books_data:
            pagination_info["first_cursor"] = books[0].get_cursor()
            pagination_info["last_cursor"] = books[-1].get_cursor()
        
        response_data = {
            "books": books_data,
            "pagination": pagination_info,
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


@book_routes.route("/books/search", methods=["GET"])
def search_books() -> tuple:

    try:

        title = request.args.get('title', '').strip()
        author = request.args.get('author', '').strip()
        genre = request.args.get('genre', '').strip()

        limit, cursor = get_cursor_pagination_params()

        query = Book.query
        
        if title:
            query = query.filter(Book.title.ilike(f'%{title}%'))
        if author:
            query = query.filter(Book.author.ilike(f'%{author}%'))
        if genre:
            query = query.filter(Book.genre.ilike(f'%{genre}%'))

        query = query.order_by(Book.created_at.desc(), Book.id.desc())

        if cursor:
            created_at, book_id = Book.parse_cursor(cursor)
            if created_at:
                query = query.filter(
                    or_(
                        Book.created_at < created_at,
                        and_(
                            Book.created_at == created_at,
                            Book.id < book_id
                        )
                    )
                )
            else:
                query = query.filter(Book.id < book_id)

        books = query.limit(limit + 1).all()
        has_next = len(books) > limit
        if has_next:
            books = books[:limit]

        books_data = [book.as_dict() for book in books]

        search_params = []
        if title:
            search_params.append(f"title={title}")
        if author:
            search_params.append(f"author={author}")
        if genre:
            search_params.append(f"genre={genre}")
        
        base_search_params = "&".join(search_params)
        base_url = request.base_url
        
        links = {}
        if books:
            if has_next:
                next_cursor = books[-1].get_cursor()
                links['next'] = f"{base_url}?{base_search_params}&limit={limit}&cursor={next_cursor}"
            
            links['first'] = f"{base_url}?{base_search_params}&limit={limit}"
        
        pagination_info = {
            "limit": limit,
            "count": len(books_data),
            "has_next": has_next,
            "cursor": cursor,
            "search_params": {
                "title": title or None,
                "author": author or None,
                "genre": genre or None
            }
        }
        
        if books_data:
            pagination_info["first_cursor"] = books[0].get_cursor()
            pagination_info["last_cursor"] = books[-1].get_cursor()
        
        response_data = {
            "books": books_data,
            "pagination": pagination_info,
            "links": links
        }
        
        return format_response(response_data)
        
    except SQLAlchemyError as e:
        return format_response({"database_error": str(e)}, 500)
    except Exception as e:
        return format_response({"server_error": str(e)}, 500)