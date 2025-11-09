from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
import os

# Prefer env var DATABASE_URL; fallback to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL") or getattr(settings, "DATABASE_URL", "sqlite:///./lostandfound.db")

# Use sync engine
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    with Session(engine) as session:
        yield session
