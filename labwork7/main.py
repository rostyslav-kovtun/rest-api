from fastapi import FastAPI
from routers import router as books_router
from auth_routers import router as auth_router
from database import connect_to_mongo, close_mongo_connection

def create_app() -> FastAPI:
    app = FastAPI(
        title="Бібліотека API з JWT автентифікацією",
        description="Лабка 7",
        version="7.0.0"
    )

    app.include_router(auth_router)
    app.include_router(books_router)

    @app.on_event("startup")
    async def startup_event():
        await connect_to_mongo()
        print("API запущено та підключено до MongoDB")
        print("Доступні ендпоінти:")
        print("- POST /auth/register - реєстрація")
        print("- POST /auth/login - вхід") 
        print("- POST /auth/refresh - оновлення токена")
        print("- GET /auth/me - інформація про користувача")
        print("- GET /api/v1/books - список книг (потрібен токен)")
        print("- Документація: http://localhost:8000/docs")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        await close_mongo_connection()
        print("Підключення до MongoDB закрито")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)