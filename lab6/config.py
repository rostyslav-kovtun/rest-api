import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'library_user')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'library_password')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'library_db')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SWAGGER = {
        'title': 'Бібліотека API',
        'uiversion': 3,
        'description': 'laba 6 :D',
        'version': '6.0.0'
    }

    BOOKS_PER_PAGE = 10