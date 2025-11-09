from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import Index

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str
    status: str = Field(default="published")  # published, draft, deleted
    
    # 失物招领专属字段
    item_type: str = Field(default="general", max_length=20)  # lost, found, general(普通帖子)
    location: Optional[str] = Field(default=None, max_length=200)  # 丢失/拾取地点
    item_time: Optional[datetime] = Field(default=None)  # 丢失/拾取时间
    contact_info: Optional[str] = Field(default=None, max_length=200)  # 联系方式（电话、微信等）
    images: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))  # 图片URL列表
    is_claimed: bool = Field(default=False)  # 是否已认领/归还
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Foreign keys
    author_id: int = Field(foreign_key="users.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")  # 物品分类
    
    # Relationships
    author: Optional["User"] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    category: Optional["Category"] = Relationship(back_populates="posts")
    claims: List["Claim"] = Relationship(back_populates="post")

    __table_args__ = (
        Index("ix_post_status", "status"),
        Index("ix_post_item_type", "item_type"),
        Index("ix_post_is_claimed", "is_claimed"),
        Index("ix_post_category_id", "category_id"),
        Index("ix_post_created_at", "created_at"),
    )

