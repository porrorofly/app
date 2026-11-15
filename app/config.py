import os
from datetime import timedelta


class Config:
    """Configuración centralizada de la Librería DAW-Books."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-desarrollo-books")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///books.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Carpeta para portadas de libros y límite de 2 MB
    UPLOAD_FOLDER = os.path.join("app", "static", "img", "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    # Duración de la sesión permanente para el carrito
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)
