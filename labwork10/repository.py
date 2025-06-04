from motor.motor_asyncio import AsyncIOMotorCollection
from models import Book, BookCreate
from database import get_database
from bson import ObjectId
from typing import List, Optional

class BookRepository:
    def __init__(self):
        self.collection_name = "books"
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_database()[self.collection_name]
    
    async def create_book(self, book_data: BookCreate) -> Book:
        book_dict = book_data.model_dump()
        result = await self.collection.insert_one(book_dict)
        
        created_book = await self.collection.find_one({"_id": result.inserted_id})
        created_book["_id"] = str(created_book["_id"])
        return Book(**created_book)
    
    async def get_all_books(self) -> List[Book]:
        books = []
        cursor = self.collection.find({})
        async for book_doc in cursor:
            book_doc["_id"] = str(book_doc["_id"])
            books.append(Book(**book_doc))
        return books
    
    async def get_book_by_id(self, book_id: str) -> Optional[Book]:
        try:
            book_doc = await self.collection.find_one({"_id": ObjectId(book_id)})
            if book_doc:
                book_doc["_id"] = str(book_doc["_id"])
                return Book(**book_doc)
            return None
        except:
            return None
    
    async def delete_book(self, book_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(book_id)})
            return result.deleted_count > 0
        except:
            return False

book_repository = BookRepository()