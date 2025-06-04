import os
from datetime import timedelta

class Settings:

    SECRET_KEY = os.getenv("SECRET_KEY", "klu4yk")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "library_db")

settings = Settings()