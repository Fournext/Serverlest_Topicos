import os
from dotenv import load_dotenv

# carga variables del .env
load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME", "ventas-service")
    ENV = os.getenv("ENV", "dev")
    PORT = int(os.getenv("PORT", "8080"))
    DATABASE_URL = os.getenv("DATABASE_URL", "")