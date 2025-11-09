from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional

class NotificationRead(BaseModel):
    id: int
    type: str
    content: str
    status: str  # 使用status字段 "unread" or "read"
    created_at: datetime
    read_at: Optional[datetime] = None
    user_id: int
    title: str = ""
    
    @computed_field
    @property
    def is_read(self) -> bool:
        """为了向后兼容前端，提供is_read属性"""
        return self.status == "read"
    
    class Config:
        from_attributes = True

