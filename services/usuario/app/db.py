import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("Falta la variable de entorno DATABASE_URL")
    return database_url


@contextmanager
def get_connection():
    conn = psycopg.connect(get_database_url(), row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id BIGSERIAL PRIMARY KEY,
        nombre VARCHAR(120) NOT NULL,
        email VARCHAR(150) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        rol VARCHAR(50) NOT NULL DEFAULT 'user',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
        conn.commit()