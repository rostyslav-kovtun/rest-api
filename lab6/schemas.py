from marshmallow import Schema, fields, validate

class BookSchema(Schema):
    id = fields.String(dump_only=True, metadata={'description': 'Унікальний ідентифікатор книги'})
    title = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=150),
        metadata={'description': 'Назва книги', 'example': 'Кобзар'}
    )
    author = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Автор книги', 'example': 'Тарас Шевченко'}
    )
    year_published = fields.Integer(
        required=True, 
        validate=validate.Range(min=1000, max=2025),
        metadata={'description': 'Рік публікації', 'example': 1840}
    )
    genre = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=50),
        metadata={'description': 'Жанр книги', 'example': 'поезія'}
    )
    created_at = fields.DateTime(dump_only=True, metadata={'description': 'Дата створення'})
    updated_at = fields.DateTime(dump_only=True, metadata={'description': 'Дата останнього оновлення'})

class PaginationSchema(Schema):
    page = fields.Integer(
        load_default=1, 
        validate=validate.Range(min=1),
        metadata={'description': 'Номер сторінки', 'example': 1}
    )
    per_page = fields.Integer(
        load_default=10, 
        validate=validate.Range(min=1, max=100),
        metadata={'description': 'Кількість елементів на сторінці', 'example': 10}
    )

class BookListResponseSchema(Schema):
    books = fields.List(fields.Nested(BookSchema), metadata={'description': 'Список книг'})
    pagination = fields.Dict(metadata={'description': 'Інформація про пагінацію'})

class ErrorResponseSchema(Schema):
    error = fields.String(metadata={'description': 'Опис помилки'})
    
class ValidationErrorResponseSchema(Schema):
    validation_errors = fields.Dict(metadata={'description': 'Помилки валідації'})

class SuccessResponseSchema(Schema):
    message = fields.String(metadata={'description': 'Повідомлення про успіх'})