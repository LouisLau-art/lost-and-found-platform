from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    """物品分类模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)  # 分类名称
    name_en: str = Field(max_length=50)  # 英文名称
    description: Optional[str] = Field(default=None, max_length=200)  # 分类描述
    icon: Optional[str] = Field(default=None, max_length=100)  # 图标名称或URL
    is_active: bool = Field(default=True)  # 是否启用
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    posts: List["Post"] = Relationship(back_populates="category")
