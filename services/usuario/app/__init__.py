from flask import Flask
from .config import Config
from .routes.health import health_bp
from .routes.usuarios import usuarios_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(health_bp)
    app.register_blueprint(usuarios_bp, url_prefix="/usuarios")

    return app