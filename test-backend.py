#!/usr/bin/env python3
"""
Simple test script to verify backend setup
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.database import create_db_and_tables
    print("✅ Database models imported successfully")
    
    create_db_and_tables()
    print("✅ Database tables created successfully")
    
    from app.main import app
    print("✅ FastAPI app created successfully")
    
    print("\n🎉 Backend setup is working!")
    print("You can now run: cd backend && python start_sqlite.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

