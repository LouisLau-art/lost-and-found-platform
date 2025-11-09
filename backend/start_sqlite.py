#!/usr/bin/env python3
"""
Startup script for the Lost & Found Platform backend with SQLite
"""
import uvicorn
from app.main import app
from app.database import create_db_and_tables

if __name__ == "__main__":
    # Create database tables
    create_db_and_tables()
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

