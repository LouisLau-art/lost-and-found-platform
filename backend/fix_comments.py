from sqlmodel import Session, select, text
from app.database import engine
import random

session = Session(engine)

print("=== Fixing comments author_id ===\n")

# Get all user IDs
user_ids = session.exec(text("SELECT id FROM users")).fetchall()
user_id_list = [uid[0] for uid in user_ids]
print(f"Found {len(user_id_list)} users")

# Get comments with NULL author_id
comments = session.exec(text("SELECT id, post_id FROM comments WHERE author_id IS NULL")).fetchall()
print(f"Found {len(comments)} comments without author_id")

if comments:
    for comment_id, post_id in comments:
        # Assign a random user as author
        random_user_id = random.choice(user_id_list)
        stmt = text("UPDATE comments SET author_id = :author_id WHERE id = :comment_id")
        session.exec(stmt.bindparams(author_id=random_user_id, comment_id=comment_id))
    
    session.commit()
    print(f"✓ Updated {len(comments)} comments with random author_id")
else:
    print("ℹ All comments already have author_id")

print("\n=== Done ===")
