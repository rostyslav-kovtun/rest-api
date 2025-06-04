from flask import Flask
from views import book_routes
from models import db, Book
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
                    title="Кобзар",
                    author="Тарас Шевченко",
                    year_published=1840,
                    genre="поезія"
                ),
                Book(
                    title="1984",
                    author="Джордж Орвелл",
                    year_published=1949,
                    genre="антиутопія"
                ),
                Book(
                    title="Норвезький ліс",
                    author="Харукі Муракамі",
                    year_published=1987,
                    genre="художня література"
                ),
                Book(
                    title="Гаррі Поттер і філософський камінь",
                    author="Дж.К. Ролінг",
                    year_published=1997,
                    genre="фентезі"
                ),
                Book(
                    title="Енеїда",
                    author="Іван Котляревський",
                    year_published=1798,
                    genre="бурлеск"
                )
            ]
            
            for book in sample_books:
                db.session.add(book)
            
            db.session.commit()
            print(f"Додано {len(sample_books)} тестових книг до бази даних")
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5050)