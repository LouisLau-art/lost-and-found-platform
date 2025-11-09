from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
from typing import List, Optional
from app.database import get_session
from app.models.user import User
from app.models.notification import Notification, NotificationStatus
from app.models.post import Post
from app.models.rating import Rating
from app.schemas.user import UserRead, UserUpdate, UserPublicRead
from app.schemas.notification import NotificationRead
from app.schemas.post import PostRead
from app.schemas.rating import RatingRead
from app.api.auth import get_current_user
from app.core.deps import get_current_admin_user

router = APIRouter()

@router.get("/profile", response_model=UserRead)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserRead)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Update user fields
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.email is not None:
        # Check if email is already taken by another user
        statement = select(User).where(User.email == user_update.email, User.id != current_user.id)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    if user_update.password is not None:
        from app.core.security import get_password_hash
        current_user.password_hash = get_password_hash(user_update.password)
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@router.get("/notifications", response_model=List[NotificationRead])
def get_user_notifications(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())
    notifications = session.exec(statement).all()
    return notifications

@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )
    notification = session.exec(statement).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.status = NotificationStatus.READ
    from datetime import datetime
    notification.read_at = datetime.utcnow()
    session.add(notification)
    session.commit()
    
    return {"message": "Notification marked as read"}

@router.get("/notifications/unread-count")
def get_unread_notification_count(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.status == NotificationStatus.UNREAD
    )
    unread_notifications = session.exec(statement).all()
    return {"unread_count": len(unread_notifications)}

# 管理员专用接口：获取所有用户列表
@router.get("/admin/list")
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name or email"),
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """管理员专用：获取所有用户列表"""
    statement = select(User).where(User.is_active == True)
    
    # 搜索功能
    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            (User.name.like(search_pattern)) | (User.email.like(search_pattern))
        )
    
    # 获取总数
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()
    
    # 获取分页数据
    statement = statement.offset(skip).limit(limit).order_by(User.created_at.desc())
    users = session.exec(statement).all()
    
    return JSONResponse(
        content={
            "data": [UserRead.model_validate(user).model_dump(mode='json') for user in users],
            "total": total
        }
    )

@router.get("/{user_id}", response_model=UserPublicRead)
def get_user_public_info(
    user_id: int,
    session: Session = Depends(get_session)
):
    """获取用户公开信息（任何人都可以访问）"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/{user_id}/posts", response_model=List[PostRead])
def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """获取用户发布的帖子列表"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    statement = select(Post).where(
        Post.author_id == user_id,
        Post.status == "published"
    ).offset(skip).limit(limit).order_by(Post.created_at.desc())
    
    posts = session.exec(statement).all()
    return posts

@router.get("/{user_id}/ratings", response_model=List[RatingRead])
def get_user_ratings(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """获取用户收到的评价列表"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    statement = select(Rating).where(
        Rating.ratee_id == user_id
    ).offset(skip).limit(limit).order_by(Rating.created_at.desc())
    
    ratings = session.exec(statement).all()
    return ratings

