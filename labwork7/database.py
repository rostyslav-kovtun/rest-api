import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def connect_to_mongo():

    db.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
    db.database = db.client[settings.DATABASE_NAME]
    print(f"Підключено до MongoDB: {settings.DATABASE_NAME}")

async def close_mongo_connection():

    if db.client:
        db.client.close()
        print("Підключення до MongoDB закрито")

def get_database() -> AsyncIOMotorDatabase:
    return db.database