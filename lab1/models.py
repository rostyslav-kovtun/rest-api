from dataclasses import dataclass, field
import uuid
from typing import Dict, Any


@dataclass
class Book:
    title: str
    author: str
    year_published: int
    genre: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def as_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year_published': self.year_published,
            'genre': self.genre
        }


library = [
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