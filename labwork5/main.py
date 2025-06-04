from fastapi import FastAPI
from routers import router
from database import connect_to_mongo, close_mongo_connection

def create_app() -> FastAPI:
    app = FastAPI(
        title="Бібліотека API з MongoDB",
        description="Лаб 5",
        version="5.0.0"
    )
    
    app.include_router(router)
    
    @app.on_event("startup")
    async def startup_event():
        await connect_to_mongo()
        print("API запущено та підключено до MongoDB")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        await close_mongo_connection()
        print("Підключення до MongoDB закрито")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)