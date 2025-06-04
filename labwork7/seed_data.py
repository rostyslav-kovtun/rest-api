import asyncio
from database import connect_to_mongo, close_mongo_connection
from repository import book_repository
from models import BookCreate

async def seed_books():
    await connect_to_mongo()

    initial_books = [
        BookCreate(
            title="Kobzar",
            author="Taras Shevchenko",
            year_published=1840,
            genre="poetry"
        ),
        BookCreate(
            title="1984",
            author="George Orwell",
            year_published=1949,
            genre="dystopian"
        ),
        BookCreate(
            title="Norwegian Wood",
            author="Haruki Murakami",
            year_published=1987,
            genre="fiction"
        )
    ]

    existing_books = await book_repository.get_all_books()
    if len(existing_books) > 0:
        print(f"База вже містить {len(existing_books)} книг.")
        print("Пропускаємо ініціалізацію.")
        await close_mongo_connection()
        return
    
    print("Додаємо початкові книги...")
    for book_data in initial_books:
        try:
            book = await book_repository.create_book(book_data)
            print(f"Додано: {book.title} by {book.author}")
        except Exception as e:
            print(f"Помилка при додаванні книги {book_data.title}: {e}")
    
    print(f"Додано {len(initial_books)} книг.")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_books())