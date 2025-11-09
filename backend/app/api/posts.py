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

router = APIRouter()

# Post endpoints
@router.post("/", response_model=PostRead)
def create_post(
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

# 智能匹配功能
@router.get("/{post_id}/matches", response_model=List[PostRead])
def get_matching_posts(
    post_id: int,
    limit: int = Query(10, ge=1, le=50),
    time_range_days: int = Query(7, ge=1, le=30, description="Time range in days for matching"),
    use_text_similarity: bool = Query(True, description="Enable text similarity matching"),
    session: Session = Depends(get_session)
):
    """
    为指定帖子查找匹配的帖子
    - 对于'lost'帖子，查找'found'帖子
    - 对于'found'帖子，查找'lost'帖子
    - 匹配条件：相同分类、相似时间、相似地点
    - 新增：文本相似度匹配（基于内容描述）
    """
    # 获取原帖子
    statement = select(Post).where(Post.id == post_id, Post.status == "published")
    original_post = session.exec(statement).first()
    
    if not original_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 只为 lost 和 found 类型的帖子提供匹配
    if original_post.item_type not in ["lost", "found"]:
        return []
    
    # 确定要匹配的类型（lost <-> found）
    target_type = "found" if original_post.item_type == "lost" else "lost"
    
    # 基础查询条件
    statement = select(Post).where(
        and_(
            Post.status.in_(["published", "active"]),
            Post.item_type == target_type,
            Post.is_claimed == False,  # 只显示未认领的
            Post.id != post_id  # 排除自身
        )
    )
    
    # 条件 1：相同分类
    if original_post.category_id:
        statement = statement.where(Post.category_id == original_post.category_id)
    
    # 条件 2：时间范围匹配
    if original_post.item_time:
        time_start = original_post.item_time - timedelta(days=time_range_days)
        time_end = original_post.item_time + timedelta(days=time_range_days)
        statement = statement.where(
            and_(
                Post.item_time.isnot(None),
                Post.item_time >= time_start,
                Post.item_time <= time_end
            )
        )
    
    # 条件 3：地点匹配（简单的模糊匹配）
    if original_post.location:
        location_pattern = f"%{original_post.location}%"
        statement = statement.where(Post.location.like(location_pattern))
    
    # 获取基础匹配结果
    statement = statement.order_by(Post.created_at.desc()).limit(limit * 3)  # 获取更多结果用于排序
    matching_posts = list(session.exec(statement).all())
    
    # 条件 4：文本相似度匹配（新增）
    if use_text_similarity and matching_posts:
        # 计算每个匹配帖子的文本相似度
        original_text = f"{original_post.title} {original_post.content}"
        
        for post in matching_posts:
            match_text = f"{post.title} {post.content}"
            similarity_score = TextSimilarityService.calculate_combined_similarity(
                original_text, 
                match_text
            )
            # 将相似度分数保存为临时属性
            post.similarity_score = similarity_score
        
        # 按相似度排序（从高到低）
        matching_posts.sort(key=lambda x: getattr(x, 'similarity_score', 0), reverse=True)
        
        # 只返回相似度大于0.1的结果
        matching_posts = [
            post for post in matching_posts 
            if getattr(post, 'similarity_score', 0) > 0.1
        ][:limit]
    else:
        # 不使用文本相似度，按时间排序
        matching_posts = matching_posts[:limit]
    
    return matching_posts

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

