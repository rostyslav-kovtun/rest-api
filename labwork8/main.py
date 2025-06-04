from fastapi import FastAPI
from routers import router as books_router
from auth_routers import router as auth_router
from database import connect_to_mongo, close_mongo_connection
from redis_client import redis_client

def create_app() -> FastAPI:
    app = FastAPI(
        title="Бібліотека API з JWT автентифікацією та Rate Limiting",
        description="labka 8",
        version="8.0.0"
    )

    app.include_router(auth_router)
    app.include_router(books_router)

    @app.on_event("startup")
    async def startup_event():
        await connect_to_mongo()
        await redis_client.connect()
        print("API запущено та підключено до MongoDB та Redis")
        print("Доступні ендпоінти:")
        print("- POST /auth/register - реєстрація")
        print("- POST /auth/login - вхід") 
        print("- POST /auth/refresh - оновлення токена")
        print("- GET /auth/me - інформація про користувача")
        print("- GET /api/v1/books/public - публічний список книг (2 req/min для анонімних, 10 для авторизованих)")
        print("- GET /api/v1/books - список книг (потрібен токен + 10 req/min)")
        print("- Документація: http://localhost:8000/docs")
        print("\nRate Limits:")
        print("- Анонімні користувачі: 2 запити за хвилину")
        print("- Авторизовані користувачі: 10 запитів за хвилину")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        await close_mongo_connection()
        await redis_client.disconnect()
        print("Підключення до MongoDB та Redis закрито")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)