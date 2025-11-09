#!/usr/bin/env python3
"""
Startup script for the Lost & Found Platform backend
"""
import asyncio
import uvicorn
from app.main import app
from app.database import init_db

if __name__ == "__main__":
    # Create database tables
    init_db()
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

