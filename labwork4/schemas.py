from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from datetime import datetime


class BookSchema(Schema):
    id = fields.String(dump_only=True)
    title = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=150, error="Назва повинна містити від 1 до 150 символів")
    )
    author = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=100, error="Автор повинен містити від 1 до 100 символів")
    )
    year_published = fields.Integer(
        required=True, 
        validate=validate.Range(
            min=1000, 
            max=datetime.now().year + 1, 
            error=f"Рік публікації повинен бути між 1000 та {datetime.now().year + 1}"
        )
    )
    genre = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=50, error="Жанр повинен містити від 1 до 50 символів")
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates_schema
    def validate_data(self, data, **kwargs):
        if 'title' in data and not data['title'].strip():
            raise ValidationError('Назва не може бути порожньою або складатися тільки з пробілів', 'title')

        if 'author' in data and not data['author'].strip():
            raise ValidationError('Автор не може бути порожнім або складатися тільки з пробілів', 'author')

        if 'genre' in data and not data['genre'].strip():
            raise ValidationError('Жанр не може бути порожнім або складатися тільки з пробілів', 'genre')


class PaginationSchema(Schema):
    limit = fields.Integer(
        missing=10,
        validate=validate.Range(min=1, max=100, error="Limit повинен бути від 1 до 100")
    )
    offset = fields.Integer(
        missing=0,
        validate=validate.Range(min=0, error="Offset не може бути негативним")
    )