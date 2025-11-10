from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
import os

# Import all models to register them with SQLModel metadata
from app.models import User, Post, Comment, Notification, Category, Claim, Rating
from app.models.claim_status_log import ClaimStatusLog
from app.models.notification import NotificationSettings

# Prefer env var DATABASE_URL; fallback to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL") or getattr(settings, "DATABASE_URL", "sqlite:///./lostandfound.db")

# Resolve SQLite relative path to absolute path under backend directory and enable check_same_thread=False
if DATABASE_URL.startswith("sqlite:///"):
    raw_path = DATABASE_URL[len("sqlite:///"): ] if DATABASE_URL.startswith("sqlite:///") else DATABASE_URL
    # Extract path after the scheme
    path_part = DATABASE_URL[len("sqlite:///"):]
    if not path_part.startswith("/"):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        abs_path = os.path.abspath(os.path.join(base_dir, path_part))
        DATABASE_URL = f"sqlite:///{abs_path}"
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )
else:
    # Use sync engine for non-sqlite
    engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    with Session(engine) as session:
        yield session
