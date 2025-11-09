
import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel, select

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.user import User
from app.models.post import Post
from app.models.claim import Claim
from app.models.category import Category
from app.models.comment import Comment
from app.core.security import get_password_hash

DATABASE_URL = "sqlite+aiosqlite:///../lostandfound.db"

fake = Faker('zh_CN')

async def get_or_create_admin(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.email == "admin@example.com"))
    admin = result.scalars().first()
    if not admin:
        hashed_password = get_password_hash("admin123")
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password_hash=hashed_password,
            is_admin=True,
            credit_score=100
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
    return admin

async def generate_users(session: AsyncSession, count: int) -> list[User]:
    users = []
    for i in range(count):
        name = fake.name()
        email = f"user{i+1}@example.com"
        result = await session.execute(select(User).where(User.email == email))
        if result.scalars().first():
            continue
        hashed_password = get_password_hash("password123")
        user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            is_admin=False,
            credit_score=random.randint(80, 100)
        )
        users.append(user)
    session.add_all(users)
    await session.commit()
    return users

async def generate_categories(session: AsyncSession) -> list[Category]:
    categories_data = [
        {"name": "电子产品", "name_en": "Electronics", "icon": "laptop"},
        {"name": "证件", "name_en": "Documents", "icon": "card"},
        {"name": "衣物", "name_en": "Clothing", "icon": "shirt"},
        {"name": "书籍", "name_en": "Books", "icon": "book"},
        {"name": "钥匙", "name_en": "Keys", "icon": "key"},
        {"name": "钱包", "name_en": "Wallets", "icon": "wallet"},
        {"name": "雨伞", "name_en": "Umbrellas", "icon": "umbrella"},
        {"name": "水杯", "name_en": "Bottles", "icon": "bottle"},
        {"name": "其他", "name_en": "Other", "icon": "other"},
    ]
    categories = []
    for cat_data in categories_data:
        result = await session.execute(select(Category).where(Category.name == cat_data["name"]))
        if not result.scalars().first():
            category = Category(**cat_data, description=f"{cat_data['name']} related items.")
            categories.append(category)
    session.add_all(categories)
    await session.commit()
    
    result = await session.execute(select(Category))
    return result.scalars().all()

async def generate_posts(session: AsyncSession, users: list[User], categories: list[Category], count: int):
    posts = []
    for _ in range(count):
        author = random.choice(users)
        category = random.choice(categories)
        post_type = random.choice(["lost", "found"])
        item_time = fake.date_time_between(start_date="-1y", end_date="now")
        
        post = Post(
            title=f"{'丢失' if post_type == 'lost' else '捡到'}了{category.name}: {fake.sentence(nb_words=4)}",
            content=fake.paragraph(nb_sentences=5),
            item_type=post_type,
            location=fake.address(),
            item_time=item_time,
            contact_info=f"Tel: {fake.phone_number()}",
            images=[fake.image_url() for _ in range(random.randint(0, 3))],
            author_id=author.id,
            category_id=category.id,
        )
        posts.append(post)
    session.add_all(posts)
    await session.commit()
    return posts

async def generate_claims_and_comments(session: AsyncSession, users: list[User], posts: list[Post]):
    claims = []
    comments = []
    for post in posts:
        # Create claims for some posts
        if random.random() < 0.5: # 50% chance to have claims
            for _ in range(random.randint(1, 3)):
                claimer = random.choice([u for u in users if u.id != post.author_id])
                claim = Claim(
                    post_id=post.id,
                    claimer_id=claimer.id,
                    message=fake.sentence(),
                    status=random.choice(["pending", "approved", "rejected"])
                )
                claims.append(claim)

        # Create comments for some posts
        if random.random() < 0.7: # 70% chance to have comments
            for _ in range(random.randint(1, 5)):
                commenter = random.choice(users)
                comment = Comment(
                    post_id=post.id,
                    author_id=commenter.id,
                    content=fake.sentence()
                )
                comments.append(comment)

    session.add_all(claims)
    session.add_all(comments)
    await session.commit()

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with AsyncSession(engine) as session:
        print("Starting data generation...")
        
        # 1. Ensure admin user exists
        admin = await get_or_create_admin(session)
        print(f"Admin user '{admin.email}' is available.")

        # 2. Generate regular users
        print("Generating users...")
        users = await generate_users(session, 50)
        all_users = [admin] + users
        print(f"Generated {len(users)} new users.")

        # 3. Generate categories
        print("Generating categories...")
        categories = await generate_categories(session)
        print(f"Generated {len(categories)} categories.")

        # 4. Generate posts
        print("Generating posts...")
        posts_to_generate = 1000
        result = await session.execute(select(Post))
        current_post_count = len(result.scalars().all())
        if current_post_count < posts_to_generate:
            new_posts = await generate_posts(session, all_users, categories, posts_to_generate - current_post_count)
            print(f"Generated {len(new_posts)} new posts.")
            
            # 5. Generate claims and comments
            print("Generating claims and comments...")
            await generate_claims_and_comments(session, all_users, new_posts)
            print("Generated claims and comments.")
        else:
            print(f"Database already has enough posts ({current_post_count}). No new data generated.")

        print("Data generation complete.")

if __name__ == "__main__":
    # Need to install faker: pip install Faker
    asyncio.run(main())
