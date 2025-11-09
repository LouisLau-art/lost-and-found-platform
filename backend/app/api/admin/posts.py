from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from typing import List
from datetime import datetime

from app.database import get_session
from app.models.user import User
from app.models.post import Post
from app.schemas.post import PostRead, PostUpdate
from app.core.deps import get_current_admin_user

router = APIRouter()


@router.get("/posts", response_model=dict)
def admin_list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    管理员获取所有帖子列表（包括已删除的）
    需要管理员权限
    """
    # 获取所有帖子（不过滤状态）
    statement = select(Post).order_by(Post.created_at.desc())
    
    # 获取总数
    count_statement = select(func.count()).select_from(Post)
    total = session.exec(count_statement).one()
    
    # 获取分页数据
    statement = statement.offset(skip).limit(limit)
    posts = session.exec(statement).all()
    
    # 返回数据
    return {
        "data": [PostRead.model_validate(post).model_dump(mode='json') for post in posts],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.delete("/posts/{post_id}")
def admin_delete_post(
    post_id: int,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    管理员删除任意帖子
    需要管理员权限
    """
    statement = select(Post).where(Post.id == post_id)
    post = session.exec(statement).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 永久删除（或者软删除）
    # 这里使用软删除
    post.status = "deleted"
    post.updated_at = datetime.utcnow()
    session.add(post)
    session.commit()
    
    return {
        "message": "Post deleted successfully",
        "post_id": post_id
    }


@router.put("/posts/{post_id}", response_model=PostRead)
def admin_update_post(
    post_id: int,
    post_update: PostUpdate,
    current_admin: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    管理员编辑任意帖子
    需要管理员权限
    """
    statement = select(Post).where(Post.id == post_id)
    post = session.exec(statement).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
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
