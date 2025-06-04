import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def connect_to_mongo():
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "library_db")

    db.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db.database = db.client[DATABASE_NAME]
    
    print(f"Підключено до MongoDB: {DATABASE_NAME}")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Підключення до MongoDB закрито")

def get_database() -> AsyncIOMotorDatabase:
    return db.database