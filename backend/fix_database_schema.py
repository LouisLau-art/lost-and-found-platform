from sqlmodel import Session, select, text
from app.database import engine
from app.models.post import Post

session = Session(engine)

print("=== Fixing database schema ===\n")

# 1. Add author_id column to comments table if it doesn't exist
print("1. Adding author_id column to comments table...")
try:
    session.exec(text("ALTER TABLE comments ADD COLUMN author_id INTEGER REFERENCES users(id)"))
    session.commit()
    print("  ✓ author_id column added successfully")
except Exception as e:
    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
        print("  ℹ author_id column already exists")
    else:
        print(f"  ✗ Error: {e}")
    session.rollback()

# 2. Fix posts with NULL content
print("\n2. Fixing posts with NULL content...")
posts = session.exec(select(Post)).all()
fixed_count = 0
for post in posts:
    if post.content is None or post.content == "":
        post.content = "无内容"  # Default content
        session.add(post)
        fixed_count += 1
if fixed_count > 0:
    session.commit()
    print(f"  ✓ Fixed {fixed_count} posts with NULL content")
else:
    print("  ℹ No posts with NULL content found")

print("\n=== Done ===")
