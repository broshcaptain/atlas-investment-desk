import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Prod: PostgreSQL (bkz. database/migrations/). Yerelde farklı bir DB için
# .env dosyasında veya ortam değişkeni olarak DATABASE_URL'i override edin
# (örn. test için sqlite:///...). Bkz. .env.example.
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg2://atlas:atlas@localhost:5432/atlas"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — istek başına bir DB oturumu açar ve kapatır."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
