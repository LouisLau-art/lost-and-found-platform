from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    credit_score: int
    is_active: bool
    is_admin: bool  # 添加管理员标识
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserPublicRead(BaseModel):
    """用户公开信息（不包含敏感信息如email）"""
    id: int
    name: str
    credit_score: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

