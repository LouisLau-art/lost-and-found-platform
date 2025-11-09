#!/usr/bin/env python3
"""
Database migration script for the Lost & Found Platform (SQLite version)
"""
import os
import sys
import sqlite3

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def migrate_database():
    """Migrate database tables"""
    print("Migrating database tables...")
    
    # Connect to the database
    conn = sqlite3.connect('lostandfound.db')
    cursor = conn.cursor()
    
    # Add missing columns to the post table
    try:
        # Add item_type column
        cursor.execute("ALTER TABLE post ADD COLUMN item_type VARCHAR(20) DEFAULT 'general'")
        print("Added item_type column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        print("item_type column already exists")
    
    try:
        # Add location column
        cursor.execute("ALTER TABLE post ADD COLUMN location VARCHAR(200)")
        print("Added location column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        print("location column already exists")
    
    try:
        # Add item_time column
        cursor.execute("ALTER TABLE post ADD COLUMN item_time DATETIME")
        print("Added item_time column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        print("item_time column already exists")
    
    try:
        # Add contact_info column
        cursor.execute("ALTER TABLE post ADD COLUMN contact_info VARCHAR(200)")
        print("Added contact_info column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        print("contact_info column already exists")
    
    try:
        # Add images column
        cursor.execute("ALTER TABLE post ADD COLUMN images JSON")
        print("Added images column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        print("images column already exists")
    
    try:
        # Add is_claimed column
        cursor.execute("ALTER TABLE post ADD COLUMN is_claimed BOOLEAN DEFAULT 0")
        print("Added is_claimed column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        print("is_claimed column already exists")
    
    try:
        # Add category_id column
        cursor.execute("ALTER TABLE post ADD COLUMN category_id INTEGER REFERENCES category(id)")
        print("Added category_id column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        print("category_id column already exists")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database migration completed successfully!")

if __name__ == "__main__":
    print("Migrating database for SQLite...")
    migrate_database()
    print("Database migration complete!")