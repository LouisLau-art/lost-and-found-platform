#!/usr/bin/env python3
"""
Database update script for the Lost & Found Platform (SQLite version)
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.database import create_db_and_tables

def update_database():
    """Update database tables"""
    print("Updating database tables...")
    create_db_and_tables()
    print("Database tables updated successfully!")

if __name__ == "__main__":
    print("Updating database for SQLite...")
    update_database()
    print("Database update complete!")