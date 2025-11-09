from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .user import UserRead

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    post_id: int
    author_id: int
    author: Optional[UserRead] = None
    
    class Config:
        from_attributes = True

