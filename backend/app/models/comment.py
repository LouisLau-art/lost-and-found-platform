from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Foreign keys
    post_id: int = Field(foreign_key="posts.id")
    author_id: int = Field(foreign_key="users.id")
    
    # Relationships
    post: Optional["Post"] = Relationship(back_populates="comments")
    author: Optional["User"] = Relationship(back_populates="comments")

