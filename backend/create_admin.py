#!/usr/bin/env python3
"""
Admin User Creation Script
Creates an administrator account for the Lost & Found Platform.
"""

import sys
import getpass
from sqlmodel import Session, select
from app.database import engine, init_db
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_user():
    """Create an admin user interactively."""
    print("=" * 60)
    print("Lost & Found Platform - Admin User Creation")
    print("=" * 60)
    print()
    
    # Initialize database
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")
    print()
    
    # Get user input
    print("Please enter the admin account details:")
    print("-" * 60)
    
    username = input("Username: ").strip()
    if not username:
        print("❌ Error: Username cannot be empty")
        sys.exit(1)
    
    name = input("Full Name: ").strip()
    if not name:
        print("❌ Error: Name cannot be empty")
        sys.exit(1)
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Error: Email cannot be empty")
        sys.exit(1)
    
    # Get password with confirmation
    while True:
        password = getpass.getpass("Password: ")
        if not password:
            print("❌ Error: Password cannot be empty")
            continue
        
        if len(password) < 6:
            print("❌ Error: Password must be at least 6 characters")
            continue
            
        password_confirm = getpass.getpass("Confirm Password: ")
        
        if password != password_confirm:
            print("❌ Error: Passwords do not match. Please try again.")
            continue
        
        break
    
    print()
    print("Creating admin user...")
    
    # Create user in database
    with Session(engine) as session:
        # Check if username already exists
        existing_user = session.exec(
            select(User).where(User.username == username)
        ).first()
        
        if existing_user:
            print(f"❌ Error: Username '{username}' already exists")
            sys.exit(1)
        
        # Check if email already exists
        existing_email = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        if existing_email:
            print(f"❌ Error: Email '{email}' is already registered")
            sys.exit(1)
        
        # Create admin user
        admin_user = User(
            username=username,
            name=name,
            email=email,
            password_hash=get_password_hash(password),
            is_admin=True,
            is_active=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print()
        print("=" * 60)
        print("✓ Admin user created successfully!")
        print("=" * 60)
        print(f"  Username: {admin_user.username}")
        print(f"  Name:     {admin_user.name}")
        print(f"  Email:    {admin_user.email}")
        print(f"  Admin:    Yes")
        print(f"  User ID:  {admin_user.id}")
        print("=" * 60)
        print()
        print("You can now login with these credentials at:")
        print("  http://localhost:5173/login")
        print()

if __name__ == "__main__":
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
