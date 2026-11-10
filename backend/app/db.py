import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# PostgreSQL is primary; with no DATABASE_URL set we fall back to a local SQLite file.
# e.g. DATABASE_URL=postgresql+psycopg://overseer:overseer@localhost:5432/overseer
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./overseer.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session():
    with SessionLocal() as session:
        yield session
