from sqlmodel import Session, select
from app.database import engine
from app.models.user import User
import re

session = Session(engine)

email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

users = session.exec(select(User)).all()
fixed_count = 0

for user in users:
    if not email_pattern.match(user.email):
        old_email = user.email
        # Fix by appending @example.com if no @ found
        if '@' not in user.email:
            user.email = f"{user.email}@example.com"
        else:
            # If @ exists but invalid, replace with valid example
            user.email = f"user{user.id}@example.com"
        
        print(f"Fixed user {user.id}: {old_email} -> {user.email}")
        session.add(user)
        fixed_count += 1

if fixed_count > 0:
    session.commit()
    print(f"\n✓ Fixed {fixed_count} invalid emails")
else:
    print("ℹ All emails are valid")
