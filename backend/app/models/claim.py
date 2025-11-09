from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Index

class Claim(SQLModel, table=True):
    __tablename__ = "claims"
    """认领请求模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 状态：pending（待确认）、approved（已确认）、rejected（已拒绝）、cancelled（已取消）
    status: str = Field(default="pending", max_length=20)
    
    # 认领说明
    message: Optional[str] = Field(default=None, max_length=500)
    
    # 物主回复
    owner_reply: Optional[str] = Field(default=None, max_length=500)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    confirmed_at: Optional[datetime] = Field(default=None)  # 确认时间
    
    # 外键
    post_id: int = Field(foreign_key="posts.id")  # 关联的帖子
    claimer_id: int = Field(foreign_key="users.id")  # 认领者
    
    # 关系
    post: Optional["Post"] = Relationship(back_populates="claims")
    
    __table_args__ = (
        Index("ix_claim_status", "status"),
        Index("ix_claim_post_id", "post_id"),
        Index("ix_claim_claimer_id", "claimer_id"),
        Index("ix_claim_created_at", "created_at"),
    )
    claimer: Optional["User"] = Relationship(
        back_populates="claims_made",
        sa_relationship_kwargs={"foreign_keys": "[Claim.claimer_id]"}
    )
    ratings: List["Rating"] = Relationship(back_populates="claim")
