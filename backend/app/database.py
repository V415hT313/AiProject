import os
from urllib.parse import quote

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()


def _build_database_url() -> str:
    # A single full DATABASE_URL takes priority, since hosted platforms
    # (Render, Railway, etc.) typically inject one directly at deploy time.
    if url := os.environ.get("DATABASE_URL"):
        return url

    user = quote(os.environ["POSTGRES_USER"], safe="")
    password = quote(os.environ["POSTGRES_PASSWORD"], safe="")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ["POSTGRES_DB"]
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


SQLALCHEMY_DATABASE_URL = _build_database_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
