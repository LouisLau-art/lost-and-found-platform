import random
import sys
from datetime import datetime, timedelta
from typing import List

from sqlmodel import Session, select, delete
from faker import Faker

from app.database import engine, init_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.category import Category
from app.models.post import Post
from app.models.comment import Comment
from app.models.claim import Claim
from app.models.notification import Notification, NotificationSettings
from app.models.claim_status_log import ClaimStatusLog
from app.models.rating import Rating

fake = Faker()
random.seed(42)

# ---- Helpers ----
def log(msg: str):
    print(f"[seed] {msg}")

# ---- Clear existing data ----
def clear_data(session: Session):
    log("Clearing existing data ...")
    # Order matters due to FKs
    session.exec(delete(Rating))
    session.exec(delete(ClaimStatusLog))
    session.exec(delete(Notification))
    session.exec(delete(Comment))
    session.exec(delete(Claim))
    session.exec(delete(Post))
    session.exec(delete(Category))
    session.exec(delete(NotificationSettings))
    session.exec(delete(User))
    session.commit()
    log("Data cleared.")

# ---- Create users ----
def create_users(session: Session, count: int = 20) -> List[User]:
    log(f"Creating 1 admin and {count} regular users ...")
    users: List[User] = []

    # Admin user
    admin = User(
        name="Admin",
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        is_admin=True,
        is_active=True,
        credit_score=100,
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    users.append(admin)

    # Regular users
    for i in range(count):
        name = fake.name()
        username = f"user{i+1}"
        email = f"user{i+1}@example.com"
        user = User(
            name=name,
            username=username,
            email=email,
            password_hash=get_password_hash("password123"),
            is_admin=False,
            is_active=True,
            credit_score=random.randint(40, 100),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        session.add(user)
        users.append(user)

    session.commit()
    # refresh ids
    for u in users:
        session.refresh(u)

    log(f"Created {len(users)} users (including admin)")
    return users

# ---- Create categories ----
def create_categories(session: Session) -> List[Category]:
    log("Creating categories ...")
    categories_data = [
        ("Electronics", "电子产品"),
        ("Documents", "证件文件"),
        ("Keys", "钥匙"),
        ("Clothing", "衣物"),
        ("Accessories", "配饰"),
        ("Books", "书籍")
    ]
    categories: List[Category] = []
    for en, zh in categories_data:
        cat = Category(name=zh, name_en=en, description=fake.sentence(nb_words=6))
        session.add(cat)
        categories.append(cat)
    session.commit()
    for c in categories:
        session.refresh(c)
    log(f"Created {len(categories)} categories")
    return categories

# ---- Create posts ----
def create_posts(session: Session, users: List[User], categories: List[Category], count: int = 50) -> List[Post]:
    log(f"Creating {count} posts ...")
    posts: List[Post] = []
    item_types = ["lost", "found", "general"]
    for _ in range(count):
        author = random.choice(users)
        item_type = random.choices(item_types, weights=[4, 4, 2])[0]
        created = datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        images = None
        if random.random() < 0.5:
            images = ["/uploads/sample1.jpg"]
            if random.random() < 0.3:
                images.append("/uploads/sample2.jpg")
        post = Post(
            title=fake.sentence(nb_words=6),
            content=fake.paragraph(nb_sentences=5),
            status="published",
            item_type=item_type,
            location=fake.city(),
            item_time=created - timedelta(hours=random.randint(0, 72)),
            contact_info=fake.phone_number(),
            images=images,
            is_claimed=False,
            author_id=author.id,
            category_id=random.choice(categories).id,
            created_at=created,
            updated_at=created
        )
        session.add(post)
        posts.append(post)
    session.commit()
    for p in posts:
        session.refresh(p)
    log(f"Created {len(posts)} posts")
    return posts

# ---- Create claims ----
def create_claims(session: Session, users: List[User], posts: List[Post], count: int = 30) -> List[Claim]:
    log(f"Creating {count} claims ...")
    claims: List[Claim] = []
    eligible_posts = [p for p in posts if p.item_type in ("lost", "found")]

    for _ in range(count):
        post = random.choice(eligible_posts)
        # pick claimer not author
        claimer = random.choice([u for u in users if u.id != post.author_id])

        status = random.choices(["pending", "approved", "rejected"], weights=[5, 2, 3])[0]
        created = post.created_at + timedelta(hours=random.randint(1, 72))
        claim = Claim(
            post_id=post.id,
            claimer_id=claimer.id,
            status=status,
            message=fake.sentence(nb_words=10) if random.random() < 0.7 else None,
            owner_reply=None,
            created_at=created,
            updated_at=created
        )

        if status == "approved":
            claim.confirmed_at = created + timedelta(hours=random.randint(1, 24))
            claim.owner_reply = fake.sentence(nb_words=8)
            # update post
            post.is_claimed = True
            post.status = "resolved"
            post.updated_at = claim.confirmed_at
            session.add(post)
        elif status == "rejected":
            claim.owner_reply = fake.sentence(nb_words=8)

        session.add(claim)
        claims.append(claim)

    session.commit()
    for c in claims:
        session.refresh(c)
    log(f"Created {len(claims)} claims")
    return claims

# ---- Create comments ----
def create_comments(session: Session, users: List[User], posts: List[Post], count: int = 100) -> List[Comment]:
    log(f"Creating {count} comments ...")
    comments: List[Comment] = []
    for _ in range(count):
        post = random.choice(posts)
        author = random.choice(users)
        created = post.created_at + timedelta(hours=random.randint(0, 96))
        comment = Comment(
            post_id=post.id,
            author_id=author.id,
            content=fake.sentence(nb_words=20),
            created_at=created,
            updated_at=created
        )
        session.add(comment)
        comments.append(comment)
    session.commit()
    for c in comments:
        session.refresh(c)
    log(f"Created {len(comments)} comments")
    return comments

# ---- Create ratings for approved claims ----
def create_ratings(session: Session, claims: List[Claim], users: List[User], max_count: int = 20):
    approved = [c for c in claims if c.status == "approved"]
    if not approved:
        log("No approved claims to rate.")
        return
    log(f"Creating up to {max_count} ratings for approved claims ...")
    created = 0
    for claim in random.sample(approved, k=min(len(approved), max_count)):
        post_owner_id = session.get(Post, claim.post_id).author_id
        # rater -> owner, ratee -> claimer OR both
        for (rater_id, ratee_id) in (
            (post_owner_id, claim.claimer_id),
            (claim.claimer_id, post_owner_id),
        ):
            rating = Rating(
                claim_id=claim.id,
                rater_id=rater_id,
                ratee_id=ratee_id,
                score=random.randint(3, 5),
                comment=fake.sentence(nb_words=12),
                created_at=claim.confirmed_at or claim.created_at
            )
            session.add(rating)
            created += 1
    session.commit()
    log(f"Created {created} ratings")


def main():
    print(
        """
##################################################################
# WARNING: THIS IS A DESTRUCTIVE SCRIPT.                         #
# IT WILL COMPLETELY WIPE ALL DATA IN YOUR DATABASE.             #
# TO PROCEED, TYPE 'yes' AND PRESS ENTER. TO CANCEL, PRESS ENTER.#
##################################################################
"""
    )
    confirm = input("Type 'yes' to continue: ").strip()
    if confirm != 'yes':
        print("Aborted. No changes were made.")
        return

    log("Initializing DB (if needed) ...")
    init_db()
    with Session(engine) as session:
        clear_data(session)
        users = create_users(session, count=20)
        categories = create_categories(session)
        posts = create_posts(session, users, categories, count=50)
        claims = create_claims(session, users, posts, count=30)
        create_comments(session, users, posts, count=100)
        create_ratings(session, claims, users, max_count=20)
        log("Seeding complete.")
        log("Admin credentials: admin@example.com / admin123")


if __name__ == "__main__":
    main()
