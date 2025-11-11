#!/usr/bin/env python3
"""
Test script to debug the Received Claims endpoint.
This script creates test data and verifies the endpoint works correctly.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.database import engine
from app.models.user import User
from app.models.post import Post
from app.models.claim import Claim
from app.models.category import Category
from app.core.security import get_password_hash
from datetime import datetime

def test_received_claims():
    """Test the received claims functionality"""
    print("\n" + "="*60)
    print("TESTING RECEIVED CLAIMS ENDPOINT")
    print("="*60)
    
    with Session(engine) as session:
        # Step 1: Create test users
        print("\n1. Creating test users...")
        
        # Post author (who will receive claims)
        author = session.exec(
            select(User).where(User.email == "author@test.com")
        ).first()
        
        if not author:
            author = User(
                username="testauthor",
                name="Test Author",
                email="author@test.com",
                password_hash=get_password_hash("test123"),
                is_active=True
            )
            session.add(author)
            session.commit()
            session.refresh(author)
        print(f"   Author created: {author.email} (ID: {author.id})")
        
        # Claimer (who will submit claims)
        claimer = session.exec(
            select(User).where(User.email == "claimer@test.com")
        ).first()
        
        if not claimer:
            claimer = User(
                username="testclaimer",
                name="Test Claimer", 
                email="claimer@test.com",
                password_hash=get_password_hash("test123"),
                is_active=True
            )
            session.add(claimer)
            session.commit()
            session.refresh(claimer)
        print(f"   Claimer created: {claimer.email} (ID: {claimer.id})")
        
        # Step 2: Create test category
        print("\n2. Creating test category...")
        category = session.exec(select(Category)).first()
        if not category:
            category = Category(
                name="测试分类",
                name_en="test",
                description="Test category"
            )
            session.add(category)
            session.commit()
            session.refresh(category)
        print(f"   Category: {category.name}")
        
        # Step 3: Create test posts by the author
        print("\n3. Creating test posts by author...")
        
        post1 = session.exec(
            select(Post).where(
                Post.author_id == author.id,
                Post.title == "Test Lost Item 1"
            )
        ).first()
        
        if not post1:
            post1 = Post(
                title="Test Lost Item 1",
                content="I lost my test item",
                item_type="lost",
                status="published",
                author_id=author.id,
                category_id=category.id,
                created_at=datetime.utcnow()
            )
            session.add(post1)
            session.commit()
            session.refresh(post1)
        print(f"   Post 1: {post1.title} (ID: {post1.id})")
        
        post2 = session.exec(
            select(Post).where(
                Post.author_id == author.id,
                Post.title == "Test Found Item 2"
            )
        ).first()
        
        if not post2:
            post2 = Post(
                title="Test Found Item 2",
                content="I found this test item",
                item_type="found",
                status="published",
                author_id=author.id,
                category_id=category.id,
                created_at=datetime.utcnow()
            )
            session.add(post2)
            session.commit()
            session.refresh(post2)
        print(f"   Post 2: {post2.title} (ID: {post2.id})")
        
        # Step 4: Create claims on author's posts
        print("\n4. Creating claims on author's posts...")
        
        # Check if claim already exists
        existing_claim1 = session.exec(
            select(Claim).where(
                Claim.post_id == post1.id,
                Claim.claimer_id == claimer.id
            )
        ).first()
        
        if not existing_claim1:
            claim1 = Claim(
                post_id=post1.id,
                claimer_id=claimer.id,
                message="I think this is mine",
                status="pending",
                created_at=datetime.utcnow()
            )
            session.add(claim1)
            session.commit()
            session.refresh(claim1)
            print(f"   Created Claim 1 on Post {post1.id}")
        else:
            print(f"   Claim 1 already exists")
            claim1 = existing_claim1
        
        existing_claim2 = session.exec(
            select(Claim).where(
                Claim.post_id == post2.id,
                Claim.claimer_id == claimer.id
            )
        ).first()
        
        if not existing_claim2:
            claim2 = Claim(
                post_id=post2.id,
                claimer_id=claimer.id,
                message="I lost this item",
                status="pending",
                created_at=datetime.utcnow()
            )
            session.add(claim2)
            session.commit()
            session.refresh(claim2)
            print(f"   Created Claim 2 on Post {post2.id}")
        else:
            print(f"   Claim 2 already exists")
            claim2 = existing_claim2
        
        # Step 5: Query claims as the author would
        print("\n5. Testing query for received claims...")
        print(f"   Querying claims for posts authored by user {author.id}...")
        
        # Get all posts by author
        author_posts = session.exec(
            select(Post).where(Post.author_id == author.id)
        ).all()
        print(f"   Found {len(author_posts)} posts by author")
        for p in author_posts:
            print(f"     - Post {p.id}: {p.title}")
        
        post_ids = [p.id for p in author_posts]
        
        # Get all claims on those posts
        received_claims = session.exec(
            select(Claim).where(Claim.post_id.in_(post_ids))
        ).all()
        
        print(f"\n   Found {len(received_claims)} claims on author's posts:")
        for claim in received_claims:
            print(f"     - Claim {claim.id}: Post {claim.post_id}, Claimer {claim.claimer_id}, Status: {claim.status}")
            print(f"       Message: {claim.message}")
        
        # Step 6: Test the API endpoint directly
        print("\n6. Testing API endpoint simulation...")
        
        # Simulate the endpoint logic
        from app.api.claims import get_received_claims
        from app.core.deps import get_session
        
        # Create a mock current_user
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        # Simulate the endpoint call
        print(f"   Simulating endpoint call as user {author.email}...")
        
        # This would be the actual endpoint logic
        # Use .all() directly to get a list of integer IDs (avoids tuple unpacking issues)
        post_ids = session.exec(
            select(Post.id).where(Post.author_id == author.id)
        ).all()
        
        if post_ids:
            claims_from_endpoint = session.exec(
                select(Claim)
                .where(Claim.post_id.in_(post_ids))
                .order_by(Claim.created_at.desc())
            ).all()
            
            print(f"   Endpoint would return {len(claims_from_endpoint)} claims")
            for c in claims_from_endpoint:
                print(f"     - Claim {c.id} on Post {c.post_id}")
        else:
            print("   No posts found for author")
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
        print("\nSummary:")
        print(f"- Author: {author.email} (ID: {author.id})")
        print(f"- Claimer: {claimer.email} (ID: {claimer.id})")
        print(f"- Posts by author: {len(author_posts)}")
        print(f"- Claims on author's posts: {len(received_claims)}")
        print("\nTo test the actual API:")
        print(f"1. Login as: {author.email} / test123")
        print("2. Navigate to /claims?tab=received")
        print("3. You should see the claims listed above")

if __name__ == "__main__":
    test_received_claims()
