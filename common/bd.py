import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.base import Base
from dotenv import load_dotenv
load_dotenv()

import models.usuario

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=0,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base.metadata.create_all(engine)