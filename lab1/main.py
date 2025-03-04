from flask import Flask
from .views import book_routes


def create_app():
    app = Flask(__name__)
    app.register_blueprint(book_routes, url_prefix='/api/v1')
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5050)