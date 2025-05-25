from flask import request
from flask_restful import Resource
from flasgger import swag_from
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from models import Book, db
from schemas import BookSchema, PaginationSchema

book_schema = BookSchema()
pagination_schema = PaginationSchema()


class BookListResource(Resource):
    
    @swag_from({
        'tags': ['Books'],
        'summary': 'Отримати всі книги',
        'description': 'Отримати список всіх книг з можливістю пагінації',
        'parameters': [
            {
                'name': 'page',
                'in': 'query',
                'type': 'integer',
                'required': False,
                'default': 1,
                'description': 'Номер сторінки'
            },
            {
                'name': 'per_page',
                'in': 'query',
                'type': 'integer',
                'required': False,
                'default': 10,
                'description': 'Кількість книг на сторінці (1-100)'
            }
        ],
        'responses': {
            200: {
                'description': 'Список книг успішно отримано',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'books': {
                            'type': 'array',
                            'items': {'$ref': '#/definitions/Book'}
                        },
                        'pagination': {
                            'type': 'object',
                            'properties': {
                                'page': {'type': 'integer'},
                                'per_page': {'type': 'integer'},
                                'total': {'type': 'integer'},
                                'pages': {'type': 'integer'},
                                'has_next': {'type': 'boolean'},
                                'has_prev': {'type': 'boolean'}
                            }
                        }
                    }
                }
            },
            422: {
                'description': 'Помилка валідації параметрів',
                'schema': {'$ref': '#/definitions/ValidationError'}
            }
        }
    })
    def get(self):
        try:
            pagination_data = pagination_schema.load(request.args)
            page = pagination_data.get('page', 1)
            per_page = pagination_data.get('per_page', 10)
            
            books_paginated = Book.query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            books_data = [book.to_dict() for book in books_paginated.items]
            
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
            
            return response_data, 200
            
        except ValidationError as e:
            return {"validation_errors": e.messages}, 422
        except SQLAlchemyError as e:
            return {"error": f"Помилка бази даних: {str(e)}"}, 500

    @swag_from({
        'tags': ['Books'],
        'summary': 'Створити нову книгу',
        'description': 'Додати нову книгу до бібліотеки',
        'parameters': [
            {
                'name': 'book',
                'in': 'body',
                'required': True,
                'schema': {'$ref': '#/definitions/BookInput'}
            }
        ],
        'responses': {
            201: {
                'description': 'Книга успішно створена',
                'schema': {'$ref': '#/definitions/Book'}
            },
            400: {
                'description': 'Невірний формат даних'
            },
            422: {
                'description': 'Помилка валідації',
                'schema': {'$ref': '#/definitions/ValidationError'}
            }
        }
    })
    def post(self):
        try:
            json_data = request.get_json()
            if not json_data:
                return {"error": "Не надано даних у форматі JSON"}, 400

            book_data = book_schema.load(json_data)
            
            new_book = Book.from_dict(book_data)
            db.session.add(new_book)
            db.session.commit()
            
            return book_schema.dump(new_book), 201
        
        except ValidationError as e:
            db.session.rollback()
            return {"validation_errors": e.messages}, 422
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Помилка бази даних: {str(e)}"}, 500


class BookResource(Resource):
    
    @swag_from({
        'tags': ['Books'],
        'summary': 'Отримати книгу за ID',
        'description': 'Отримати інформацію про конкретну книгу',
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'string',
                'required': True,
                'description': 'Унікальний ідентифікатор книги'
            }
        ],
        'responses': {
            200: {
                'description': 'Інформація про книгу',
                'schema': {'$ref': '#/definitions/Book'}
            },
            404: {
                'description': 'Книгу не знайдено',
                'schema': {'$ref': '#/definitions/Error'}
            }
        }
    })
    def get(self, book_id):
        try:
            book = Book.query.get(book_id)
            if not book:
                return {"error": f"Книгу з ID {book_id} не знайдено"}, 404
            return book_schema.dump(book), 200
        except SQLAlchemyError as e:
            return {"error": f"Помилка бази даних: {str(e)}"}, 500

    @swag_from({
        'tags': ['Books'],
        'summary': 'Оновити книгу',
        'description': 'Оновити інформацію про книгу',
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'string',
                'required': True,
                'description': 'Унікальний ідентифікатор книги'
            },
            {
                'name': 'book',
                'in': 'body',
                'required': True,
                'schema': {'$ref': '#/definitions/BookInput'}
            }
        ],
        'responses': {
            200: {
                'description': 'Книга успішно оновлена',
                'schema': {'$ref': '#/definitions/Book'}
            },
            400: {
                'description': 'Невірний формат даних'
            },
            404: {
                'description': 'Книгу не знайдено'
            },
            422: {
                'description': 'Помилка валідації'
            }
        }
    })
    def put(self, book_id):
        try:
            book = Book.query.get(book_id)
            if not book:
                return {"error": f"Книгу з ID {book_id} не знайдено"}, 404
            
            json_data = request.get_json()
            if not json_data:
                return {"error": "Не надано даних у форматі JSON"}, 400

            book_data = book_schema.load(json_data, partial=True)
            
            for field, value in book_data.items():
                setattr(book, field, value)
            
            db.session.commit()
            
            return book_schema.dump(book), 200
        
        except ValidationError as e:
            db.session.rollback()
            return {"validation_errors": e.messages}, 422
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Помилка бази даних: {str(e)}"}, 500

    @swag_from({
        'tags': ['Books'],
        'summary': 'Видалити книгу',
        'description': 'Видалити книгу з бібліотеки',
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'string',
                'required': True,
                'description': 'Унікальний ідентифікатор книги'
            }
        ],
        'responses': {
            200: {
                'description': 'Книга успішно видалена',
                'schema': {'$ref': '#/definitions/Success'}
            },
            404: {
                'description': 'Книгу не знайдено',
                'schema': {'$ref': '#/definitions/Error'}
            }
        }
    })
    def delete(self, book_id):
        try:
            book = Book.query.get(book_id)
            if not book:
                return {"error": f"Книгу з ID {book_id} не знайдено"}, 404
            
            book_title = book.title
            db.session.delete(book)
            db.session.commit()
            
            return {"message": f"Книгу '{book_title}' видалено"}, 200
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Помилка бази даних: {str(e)}"}, 500