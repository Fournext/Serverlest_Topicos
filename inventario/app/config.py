import os


class Config:
    APP_NAME = os.getenv("APP_NAME", "ventas-service")
    ENV = os.getenv("ENV", "dev")
    PORT = int(os.getenv("PORT", "8080"))

    DB_USER = os.getenv("DB_USER", "")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_NAME = os.getenv("DB_NAME", "")
    DB_HOST = os.getenv("DB_HOST", "")