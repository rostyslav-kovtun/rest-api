import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_USER = os.getenv('MONGO_USER', 'mongo_admin')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'password')
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'library_db')

    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"

    BOOKS_COLLECTION = "books"