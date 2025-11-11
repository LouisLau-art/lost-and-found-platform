from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, or_, and_, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_session
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.notification import Notification
from app.schemas.post import PostCreate, PostRead, PostUpdate
from app.schemas.comment import CommentCreate, CommentRead
from app.core.deps import get_current_user
from app.services.notification_service import NotificationService
from app.services.text_similarity import TextSimilarityService
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
import numpy as np

router = APIRouter()

# Post endpoints
@router.post("/", response_model=PostRead)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_post = Post(
        title=post.title,
        content=post.content,
        item_type=post.item_type,
        location=post.location,
        item_time=post.item_time,
        contact_info=post.contact_info,
        category_id=post.category_id,
        images=post.images,
        author_id=current_user.id
    )
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    
    # Smart matching: Find potential matches and notify relevant users
    if db_post.item_type in ["lost", "found"]:
        # Determine target type (lost <-> found)
        target_type = "found" if db_post.item_type == "lost" else "lost"
        
        # Build query for matching posts
        match_query = select(Post).where(
            and_(
                Post.status.in_(["published", "active"]),
                Post.item_type == target_type,
                Post.is_claimed == False,
                Post.id != db_post.id
            )
        )
        
        # Filter by category if available
        if db_post.category_id:
            match_query = match_query.where(Post.category_id == db_post.category_id)
        
        # Filter by location if available
        if db_post.location:
            location_pattern = f"%{db_post.location}%"
            match_query = match_query.where(Post.location.like(location_pattern))
        
        # Filter by time range (7 days) if available
        if db_post.item_time:
            time_start = db_post.item_time - timedelta(days=7)
            time_end = db_post.item_time + timedelta(days=7)
            match_query = match_query.where(
                and_(
                    Post.item_time.isnot(None),
                    Post.item_time >= time_start,
                    Post.item_time <= time_end
                )
            )
        
        # Get potential matches
        match_query = match_query.order_by(Post.created_at.desc()).limit(10)
        potential_matches = list(session.exec(match_query).all())
        
        # Calculate similarity scores and notify if high match found
        if potential_matches:
            new_post_text = f"{db_post.title} {db_post.content}"
            
            for match_post in potential_matches:
                match_text = f"{match_post.title} {match_post.content}"
                similarity_score = TextSimilarityService.calculate_combined_similarity(
                    new_post_text,
                    match_text
                )
                
                # Notify if similarity is above threshold (0.3 = 30%)
                if similarity_score > 0.3:
                    # Notify the author of the matching post
                    await NotificationService.create_matching_notification(
                        session=session,
                        user_id=match_post.author_id,
                        new_post=db_post,
                        matched_post=match_post,
                        similarity_score=similarity_score
                    )
    
    return db_post

@router.get("/")
def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    item_type: Optional[str] = Query(None, description="Filter by item_type: lost, found, general"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_claimed: Optional[bool] = Query(None, description="Filter by claimed status"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    session: Session = Depends(get_session)
):
    statement = select(Post).where(Post.status.in_(["published", "active"]))
    
    # 筛选条件
    if item_type:
        statement = statement.where(Post.item_type == item_type)
    if category_id:
        statement = statement.where(Post.category_id == category_id)
    if is_claimed is not None:
        statement = statement.where(Post.is_claimed == is_claimed)
    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            (Post.title.like(search_pattern)) | (Post.content.like(search_pattern))
        )
    
    # 获取总数
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()
    
    # 获取分页数据
    statement = statement.offset(skip).limit(limit).order_by(Post.created_at.desc())
    posts = session.exec(statement).all()
    
    # 返回JSON响应，包含总数
    return JSONResponse(
        content={
            "data": [PostRead.model_validate(post).model_dump(mode='json') for post in posts],
            "total": total
        }
    )

@router.get("/{post_id}", response_model=PostRead)
def get_post(
    post_id: int,
    session: Session = Depends(get_session)
):
    statement = select(Post).where(Post.id == post_id, Post.status.in_(["published", "active"]))
    post = session.exec(statement).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post

@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Post).where(Post.id == post_id, Post.author_id == current_user.id)
    post = session.exec(statement).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to edit it"
        )
    
    # 更新所有可能的字段
    update_data = post_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    post.updated_at = datetime.utcnow()
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Post).where(Post.id == post_id, Post.author_id == current_user.id)
    post = session.exec(statement).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    
    # Soft delete by changing status
    post.status = "deleted"
    post.updated_at = datetime.utcnow()
    session.add(post)
    session.commit()
    
    return {"message": "Post deleted successfully"}

# Comment endpoints
@router.post("/{post_id}/comments", response_model=CommentRead)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if post exists
    statement = select(Post).where(Post.id == post_id, Post.status.in_(["published", "active"]))
    post = session.exec(statement).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Create comment
    db_comment = Comment(
        content=comment.content,
        post_id=post_id,
        author_id=current_user.id
    )
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    
    # Create notification for post author (if not the same user)
    if post.author_id != current_user.id:
        await NotificationService.create_comment_notification(session, db_comment, post)
    
    return db_comment

@router.get("/{post_id}/comments", response_model=List[CommentRead])
def list_comments(
    post_id: int,
    session: Session = Depends(get_session)
):
    statement = select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    comments = session.exec(statement).all()
    return comments

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Comment).where(Comment.id == comment_id, Comment.author_id == current_user.id)
    comment = session.exec(statement).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )
    
    session.delete(comment)
    session.commit()
    
    return {"message": "Comment deleted successfully"}

# 智能匹配功能 V2.0 - TF-IDF Based Matching
@router.get("/{post_id}/matches", response_model=List[PostRead])
def get_matching_posts(
    post_id: int,
    limit: int = Query(10, ge=1, le=50),
    time_range_days: int = Query(7, ge=1, le=30, description="Time range in days for matching"),
    session: Session = Depends(get_session)
):
    """
    Advanced matching algorithm using TF-IDF and multi-dimensional scoring.
    
    Weights:
    - Text Similarity (TF-IDF): 50%
    - Category Match: 20%
    - Location Proximity: 15%
    - Time Proximity: 15%
    """
    # 1) Get original post
    statement = select(Post).where(Post.id == post_id, Post.status == "published")
    original_post = session.exec(statement).first()
    
    if not original_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 2) Only match for lost and found posts
    if original_post.item_type not in ["lost", "found"]:
        return []
    
    # Determine target type (lost <-> found)
    target_type = "found" if original_post.item_type == "lost" else "lost"
    
    # 3) Get all potential candidates (broader search)
    statement = select(Post).where(
        and_(
            Post.status.in_(["published", "active"]),
            Post.item_type == target_type,
            Post.is_claimed == False,
            Post.id != post_id
        )
    )
    
    # Get all candidates for scoring (up to 100)
    statement = statement.order_by(Post.created_at.desc()).limit(100)
    candidates = list(session.exec(statement).all())
    
    if not candidates:
        return []
    
    # 4) Calculate multi-dimensional scores
    scored_posts = []
    
    # Prepare TF-IDF vectorizer
    all_texts = [f"{original_post.title} {original_post.content}"]
    all_texts.extend([f"{post.title} {post.content}" for post in candidates])
    
    try:
        # Use TF-IDF for text similarity
        vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 2),  # Use both unigrams and bigrams
            stop_words=None  # We'll keep all words for Chinese text
        )
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity between original and all candidates
        original_vector = tfidf_matrix[0:1]
        candidate_vectors = tfidf_matrix[1:]
        text_similarities = cosine_similarity(original_vector, candidate_vectors).flatten()
    except:
        # Fallback to simple similarity if TF-IDF fails
        text_similarities = []
        original_text = all_texts[0]
        for post in candidates:
            match_text = f"{post.title} {post.content}"
            sim = TextSimilarityService.calculate_combined_similarity(original_text, match_text)
            text_similarities.append(sim)
        text_similarities = np.array(text_similarities)
    
    # Calculate scores for each candidate
    for idx, post in enumerate(candidates):
        # a) Text Similarity Score (50% weight)
        text_score = float(text_similarities[idx]) * 100  # Convert to 0-100 scale
        
        # b) Category Match Score (20% weight)
        category_score = 100 if (original_post.category_id and 
                                 original_post.category_id == post.category_id) else 0
        
        # c) Location Proximity Score (15% weight)
        location_score = 0
        if original_post.location and post.location:
            try:
                # Use Levenshtein distance for string similarity
                distance = Levenshtein.distance(original_post.location.lower(), 
                                               post.location.lower())
                max_len = max(len(original_post.location), len(post.location))
                location_score = (1 - distance / max_len) * 100 if max_len > 0 else 0
            except:
                # Fallback to simple containment check
                if original_post.location.lower() in post.location.lower() or \
                   post.location.lower() in original_post.location.lower():
                    location_score = 50
        
        # d) Time Proximity Score (15% weight)
        time_score = 0
        if original_post.item_time and post.item_time:
            # For lost->found: found time should be after lost time
            # For found->lost: lost time should be before found time
            time_diff = abs((post.item_time - original_post.item_time).days)
            
            if original_post.item_type == "lost" and post.item_time < original_post.item_time:
                # Found before lost - invalid
                time_score = 0
            elif original_post.item_type == "found" and post.item_time > original_post.item_time:
                # Lost after found - invalid  
                time_score = 0
            else:
                # Linear decay: 100 points for same day, 0 points for 7+ days
                time_score = max(0, (1 - time_diff / time_range_days) * 100)
        
        # Calculate weighted final score
        final_score = (text_score * 0.50 + 
                      category_score * 0.20 + 
                      location_score * 0.15 + 
                      time_score * 0.15)
        
        # Store score as temporary attribute
        post.similarity_score = round(final_score, 2)
        scored_posts.append((final_score, post))
    
    # 5) Sort by score and filter
    scored_posts.sort(key=lambda x: x[0], reverse=True)
    
    # Only return posts with score > 10 (minimum threshold)
    result_posts = [post for score, post in scored_posts if score > 10][:limit]
    
    return result_posts

@router.get("/search/advanced", response_model=List[PostRead])
def advanced_search(
    item_type: Optional[str] = Query(None, description="lost or found"),
    category_id: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    is_claimed: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """
    高级搜索功能
    支持多条件组合搜索
    """
    statement = select(Post).where(Post.status.in_(["published", "active"]))
    
    if item_type:
        statement = statement.where(Post.item_type == item_type)
    
    if category_id:
        statement = statement.where(Post.category_id == category_id)
    
    if location:
        location_pattern = f"%{location}%"
        statement = statement.where(Post.location.like(location_pattern))
    
    if start_date:
        statement = statement.where(Post.item_time >= start_date)
    
    if end_date:
        statement = statement.where(Post.item_time <= end_date)
    
    statement = statement.where(Post.is_claimed == is_claimed)
    
    statement = statement.offset(skip).limit(limit).order_by(Post.created_at.desc())
    posts = session.exec(statement).all()
    
    return posts

