from flask_sqlalchemy import SQLAlchemy
from typing import Dict, Any
import uuid

db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __init__(self, title: str, author: str, year_published: int, genre: str):
        self.title = title
        self.author = author
        self.year_published = year_published
        self.genre = genre
    
    def as_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year_published': self.year_published,
            'genre': self.genre,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'