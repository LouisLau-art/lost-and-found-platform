#!/usr/bin/env python3
"""
Database initialization script for the Lost & Found Platform
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def create_database():
    """Create the database if it doesn't exist"""
    # Extract database name from URL
    db_url = settings.DATABASE_URL
    if db_url.startswith('postgresql://'):
        # Parse the URL to get database name
        parts = db_url.split('/')
        db_name = parts[-1]
        base_url = '/'.join(parts[:-1])
        
        # Connect to postgres database to create our database
        engine = create_engine(base_url + '/postgres')
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"Database '{db_name}' created successfully!")
            else:
                print(f"Database '{db_name}' already exists.")
    else:
        print("This script only supports PostgreSQL databases.")

def create_tables():
    """Create all tables"""
    from app.database import create_db_and_tables
    create_db_and_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    print("Initializing database...")
    create_database()
    create_tables()
    print("Database initialization complete!")

