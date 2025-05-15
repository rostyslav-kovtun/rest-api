from typing import List, Optional
from datetime import datetime
from pydantic_mongo import PydanticObjectId
from database import get_books_collection
from models import Book, BookCreate, BookUpdate


async def create_book(book_data: BookCreate) -> Book:
    collection = get_books_collection()

    book_dict = book_data.model_dump()
    book_dict["created_at"] = datetime.utcnow()
    book_dict["updated_at"] = datetime.utcnow()

    result = await collection.insert_one(book_dict)

    created_book = await collection.find_one({"_id": result.inserted_id})
    return Book(**created_book)


async def get_all_books(skip: int = 0, limit: int = 10) -> List[Book]:
    collection = get_books_collection()

    cursor = collection.find({}).skip(skip).limit(limit).sort("created_at", 1)
    books = []
    
    async for book_doc in cursor:
        books.append(Book(**book_doc))
    
    return books


async def get_book_by_id(book_id: str) -> Optional[Book]:
    collection = get_books_collection()
    
    try:
        object_id = PydanticObjectId(book_id)
        book_doc = await collection.find_one({"_id": object_id})
        
        if book_doc:
            return Book(**book_doc)
        return None
    except Exception:
        return None


async def update_book(book_id: str, book_data: BookUpdate) -> Optional[Book]:
    collection = get_books_collection()
    
    try:
        object_id = PydanticObjectId(book_id)

        update_data = {}
        for field, value in book_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            return await get_book_by_id(book_id)
        
        update_data["updated_at"] = datetime.utcnow()

        await collection.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )

        return await get_book_by_id(book_id)
    except Exception:
        return None


async def delete_book(book_id: str) -> bool:
    collection = get_books_collection()
    
    try:
        object_id = PydanticObjectId(book_id)
        result = await collection.delete_one({"_id": object_id})

        return result.deleted_count > 0
    except Exception:
        return False


async def get_books_count() -> int:
    collection = get_books_collection()
    return await collection.count_documents({})