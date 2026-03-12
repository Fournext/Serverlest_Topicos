import os


class Config:
    APP_NAME = os.getenv("APP_NAME", "usuarios-service")
    ENV = os.getenv("ENV", "dev")
    PORT = int(os.getenv("PORT", "8080"))