import motor.motor_asyncio
from config import Config


class MongoDB:
    client = None
    database = None


async def connect_to_mongo():
    MongoDB.client = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI)
    MongoDB.database = MongoDB.client[Config.MONGO_DB]
    print(f"Підключено до MongoDB: {Config.MONGO_DB}")


async def close_mongo_connection():
    if MongoDB.client:
        MongoDB.client.close()
        print("Відключено від MongoDB")


def get_database():
    return MongoDB.database


def get_books_collection():
    database = get_database()
    return database[Config.BOOKS_COLLECTION]