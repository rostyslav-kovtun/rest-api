from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Book
from views import book_routes
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(book_routes, url_prefix='/api/v1')

    with app.app_context():
        db.create_all()

        if Book.query.count() == 0:
            sample_books = [
                Book(
                    title="Kobzar",
                    author="Taras Shevchenko",
                    year_published=1840,
                    genre="poetry"
                ),
                Book(
                    title="1984",
                    author="George Orwell",
                    year_published=1949,
                    genre="dystopian"
                ),
                Book(
                    title="Norwegian Wood",
                    author="Haruki Murakami",
                    year_published=1987,
                    genre="fiction"
                )
            ]
            
            for book in sample_books:
                db.session.add(book)
            
            db.session.commit()
            print("Початкові дані додано до бази даних")
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)