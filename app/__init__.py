from flask import Flask, render_template
from app.config import Config
from app.models import db, login_manager, Libro, Usuario


def create_app(config_class=Config):
    """Factoría de aplicaciones de DAW-Books."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.blueprints.public import public_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # Manejador de error 403 (Acceso Prohibido)
    @app.errorhandler(403)
    def acceso_prohibido(e):
        return render_template("403.html"), 403
    # Manejador de error 404(Enlace que no existe)
    @app.errorhandler(404)
    def error_de_pagina(e):
        return render_template("404.html"), 404
    

    with app.app_context():
        db.create_all()

        # Semilla inicial de libros
        if not Libro.query.first():
            db.session.add_all(
                [
                    Libro(titulo="Don Quijote de la Mancha", autor="Miguel de Cervantes",
                          genero="Novela", precio=18.50, stock=8),
                    Libro(titulo="Dune", autor="Frank Herbert",
                          genero="Ciencia ficción", precio=22.90, stock=5),
                    Libro(titulo="Clean Code", autor="Robert C. Martin",
                          genero="Informática", precio=35.00, stock=0),  # Agotado para pruebas
                    Libro(titulo="Fundación", autor="Isaac Asimov",
                          genero="Ciencia ficción", precio=19.90, stock=3),
                    Libro(titulo="Flask Web Development", autor="Miguel Grinberg",
                          genero="Informática", precio=39.90, stock=4),
                ]
            )
            db.session.commit()

        # Semilla inicial de usuarios (Gestor y Cliente)
        if not Usuario.query.first():
            gestor = Usuario(username="gestor_jefe", email="gestor@dawbooks.com",
                             edad=40, rol="gestor")
            gestor.set_password("gestor123")

            cliente = Usuario(username="cliente_laura", email="cliente@dawbooks.com",
                              edad=27, rol="cliente")
            cliente.set_password("cliente123")

            db.session.add_all([gestor, cliente])
            db.session.commit()

    return app
