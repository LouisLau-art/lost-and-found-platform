from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    credit_score: int = Field(default=100)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)  # 管理员权限标识
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    notifications: List["Notification"] = Relationship(back_populates="user")
    claims_made: List["Claim"] = Relationship(
        back_populates="claimer",
        sa_relationship_kwargs={"foreign_keys": "[Claim.claimer_id]"}
    )
    ratings_given: List["Rating"] = Relationship(
        back_populates="rater",
        sa_relationship_kwargs={"foreign_keys": "[Rating.rater_id]"}
    )
    ratings_received: List["Rating"] = Relationship(
        back_populates="ratee",
        sa_relationship_kwargs={"foreign_keys": "[Rating.ratee_id]"}
    )

