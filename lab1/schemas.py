from marshmallow import Schema, fields, validate


class BookSchema(Schema):
    id = fields.String(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    author = fields.String(required=True, validate=validate.Length(min=1, max=100))
    year_published = fields.Integer(required=True, validate=validate.Range(min=1000, max=2025))
    genre = fields.String(required=True, validate=validate.Length(min=1, max=50))