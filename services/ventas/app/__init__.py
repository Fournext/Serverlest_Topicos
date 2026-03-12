from flask import Flask
from .config import Config
from .db import init_db
from .routes.health import health_bp
from .routes.ventas import ventas_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db()

    app.register_blueprint(health_bp)
    app.register_blueprint(ventas_bp, url_prefix="/ventas")

    return app