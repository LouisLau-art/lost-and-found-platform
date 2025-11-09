from sqlmodel import Session, select
from app.database import engine
from app.models.post import Post
from app.schemas.post import PostRead
import json

session = Session(engine)

# Get one post
posts = session.exec(select(Post).limit(3)).all()
print(f"Found {len(posts)} posts\n")

for post in posts:
    print(f"=== Post ID: {post.id} ===")
    print(f"Title: {post.title}")
    print(f"Status: {post.status}")
    print(f"Author ID: {post.author_id}")
    print(f"Category ID: {post.category_id}")
    
    try:
        # Try to validate
        post_read = PostRead.model_validate(post)
        print("✓ Validation SUCCESS")
        
        # Try to dump
        data = post_read.model_dump(mode='json')
        print(f"✓ Serialization SUCCESS")
        print(f"Keys: {list(data.keys())}")
    except Exception as e:
        print(f"✗ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print()
