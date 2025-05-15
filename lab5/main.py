from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routers import router
import crud
from models import BookCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()

    books_count = await crud.get_books_count()
    if books_count == 0:
        sample_books = [
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
        
        for book_data in sample_books:
            await crud.create_book(book_data)
        
        print("Початкові дані додано до MongoDB")
    
    yield

    await close_mongo_connection()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Бібліотека API (FastAPI + MongoDB)",
        description="лаба 5",
        version="5.0.0",
        lifespan=lifespan
    )
    
    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)