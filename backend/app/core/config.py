from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database (sync SQLite for SQLModel Session)
    DATABASE_URL: str = "sqlite:///./lostandfound.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ]
    
    # App
    PROJECT_NAME: str = "Lost & Found Platform"
    
    class Config:
        env_file = ".env"

settings = Settings()

