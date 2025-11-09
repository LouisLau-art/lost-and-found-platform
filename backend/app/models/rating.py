from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Rating(SQLModel, table=True):
    """评价模型 - 认领成功后的双方评价"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 评分（1-5星）
    score: int = Field(ge=1, le=5)
    
    # 评价内容
    comment: Optional[str] = Field(default=None, max_length=500)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 外键
    claim_id: int = Field(foreign_key="claims.id")  # 关联的认领请求
    rater_id: int = Field(foreign_key="users.id")  # 评价者
    ratee_id: int = Field(foreign_key="users.id")  # 被评价者
    
    # 关系
    claim: Optional["Claim"] = Relationship(back_populates="ratings")
    rater: Optional["User"] = Relationship(
        back_populates="ratings_given",
        sa_relationship_kwargs={"foreign_keys": "[Rating.rater_id]"}
    )
    ratee: Optional["User"] = Relationship(
        back_populates="ratings_received",
        sa_relationship_kwargs={"foreign_keys": "[Rating.ratee_id]"}
    )
