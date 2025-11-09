from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .comment import CommentRead
from .user import UserRead
from .category import CategoryRead

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    item_type: str = Field(default="general", pattern="^(lost|found|general)$")  # 类型限制
    location: Optional[str] = Field(default=None, max_length=200)
    item_time: Optional[datetime] = None
    contact_info: Optional[str] = Field(default=None, max_length=200)
    category_id: Optional[int] = Field(default=None, gt=0)

class PostCreate(PostBase):
    images: Optional[List[str]] = None  # 图片URL列表

class PostRead(PostBase):
    id: int
    status: str
    images: Optional[List[str]] = None
    is_claimed: bool
    created_at: datetime
    updated_at: Optional[datetime]
    author_id: int
    author: Optional[UserRead] = None
    category: Optional[CategoryRead] = None
    comments: List[CommentRead] = []
    
    class Config:
        from_attributes = True

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    item_type: Optional[str] = None
    location: Optional[str] = None
    item_time: Optional[datetime] = None
    contact_info: Optional[str] = None
    category_id: Optional[int] = None
    images: Optional[List[str]] = None
    is_claimed: Optional[bool] = None

