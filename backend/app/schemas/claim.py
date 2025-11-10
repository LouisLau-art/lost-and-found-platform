from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .user import UserRead

class ClaimBase(BaseModel):
    message: Optional[str] = Field(default=None, max_length=500)

class ClaimCreate(ClaimBase):
    post_id: int = Field(gt=0)

class PostReadInClaim(BaseModel):
    """Minimal Post fields embedded in Claim responses"""
    id: int
    title: str
    images: Optional[List[str]] = None

    class Config:
        from_attributes = True

class ClaimRead(ClaimBase):
    id: int
    status: str
    owner_reply: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime
    updated_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    post_id: int
    claimer_id: int
    claimer: Optional[UserRead] = None
    post: Optional[PostReadInClaim] = None
    
    class Config:
        from_attributes = True

class ClaimUpdate(BaseModel):
    status: Optional[str] = None
    owner_reply: Optional[str] = Field(default=None, max_length=500)

class ClaimApprove(BaseModel):
    owner_reply: Optional[str] = Field(default=None, max_length=500)

class ClaimReject(BaseModel):
    owner_reply: Optional[str] = Field(default=None, max_length=500)
