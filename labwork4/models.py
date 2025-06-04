from flask_sqlalchemy import SQLAlchemy
from typing import Dict, Any
import uuid
from datetime import datetime

db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    __table_args__ = (
        db.Index('idx_books_created_at_id', 'created_at', 'id'),
        db.Index('idx_books_created_at', 'created_at'),
    )
    
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
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cursor': self.get_cursor()
        }
    
    def get_cursor(self) -> str:
        if self.created_at:

            timestamp = int(self.created_at.timestamp() * 1000000)
            return f"{timestamp}_{self.id}"
        return self.id
    
    @staticmethod
    def parse_cursor(cursor: str) -> tuple:
        try:
            if '_' in cursor:
                timestamp_str, book_id = cursor.split('_', 1)
                timestamp = int(timestamp_str)
                created_at = datetime.fromtimestamp(timestamp / 1000000)
                return created_at, book_id
            else:

                return None, cursor
        except (ValueError, TypeError):
            return None, cursor
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'