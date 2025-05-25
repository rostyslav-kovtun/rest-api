from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from models import db, Book
from resources import BookListResource, BookResource
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    api = Api(app, prefix='/api/v1')

    api.add_resource(BookListResource, '/books')
    api.add_resource(BookResource, '/books/<string:book_id>')
    
    swagger = Swagger(app)
    
    swagger.template = {
        "swagger": "2.0",
        "info": {
            "title": "Бібліотека API",
            "description": "лабка 6",
            "version": "6.0.0"
        },
        "host": "localhost:5000",
        "basePath": "/api/v1",
        "schemes": ["http"],
        "definitions": {
            "Book": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Унікальний ідентифікатор книги"
                    },
                    "title": {
                        "type": "string",
                        "description": "Назва книги",
                        "example": "Кобзар"
                    },
                    "author": {
                        "type": "string",
                        "description": "Автор книги",
                        "example": "Тарас Шевченко"
                    },
                    "year_published": {
                        "type": "integer",
                        "description": "Рік публікації",
                        "example": 1840
                    },
                    "genre": {
                        "type": "string",
                        "description": "Жанр книги",
                        "example": "поезія"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Дата створення"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Дата останнього оновлення"
                    }
                }
            },
            "BookInput": {
                "type": "object",
                "required": ["title", "author", "year_published", "genre"],
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Назва книги",
                        "example": "Нова книга"
                    },
                    "author": {
                        "type": "string",
                        "description": "Автор книги",
                        "example": "Новий автор"
                    },
                    "year_published": {
                        "type": "integer",
                        "description": "Рік публікації",
                        "minimum": 1000,
                        "maximum": 2025,
                        "example": 2024
                    },
                    "genre": {
                        "type": "string",
                        "description": "Жанр книги",
                        "example": "фантастика"
                    }
                }
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Опис помилки"
                    }
                }
            },
            "ValidationError": {
                "type": "object",
                "properties": {
                    "validation_errors": {
                        "type": "object",
                        "description": "Помилки валідації полів"
                    }
                }
            },
            "Success": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Повідомлення про успіх"
                    }
                }
            }
        }
    }
    
    with app.app_context():
        db.create_all()

        if Book.query.count() == 0:
            sample_books = [
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
            
            for book in sample_books:
                db.session.add(book)
            
            db.session.commit()
            print("Початкові дані додано до бази даних")
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)