from sqlmodel import Session, select
from app.database import engine
from app.models.post import Post
from app.schemas.post import PostRead

session = Session(engine)
posts = session.exec(select(Post).limit(1)).all()
print(f'Total posts: {len(posts)}')

if posts:
    post = posts[0]
    print(f'\nPost ID: {post.id}')
    print(f'Title: {post.title}')
    print(f'Author ID: {post.author_id}')
    print(f'Category ID: {post.category_id}')
    
    # Check if relationships are loaded
    print(f'\nHas author attr: {hasattr(post, "author")}')
    if hasattr(post, 'author'):
        print(f'Author loaded: {post.author is not None}')
        if post.author:
            print(f'Author name: {post.author.name}')
            print(f'Author has is_admin: {hasattr(post.author, "is_admin")}')
            if hasattr(post.author, 'is_admin'):
                print(f'Author is_admin value: {post.author.is_admin}')
    
    print(f'\nHas category attr: {hasattr(post, "category")}')
    if hasattr(post, 'category'):
        print(f'Category loaded: {post.category is not None}')
        if post.category:
            print(f'Category name: {post.category.name}')
            print(f'Category name_en: {post.category.name_en}')
    
    # Try to validate
    print('\n=== Attempting to validate ===')
    try:
        post_read = PostRead.model_validate(post)
        print('SUCCESS!')
        print(f'PostRead: {post_read.model_dump()}')
    except Exception as e:
        print(f'ERROR: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
