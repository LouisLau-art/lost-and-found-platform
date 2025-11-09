from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .user import UserRead

class RatingBase(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class RatingCreate(RatingBase):
    claim_id: int
    ratee_id: int

class RatingRead(RatingBase):
    id: int
    created_at: datetime
    claim_id: int
    rater_id: int
    ratee_id: int
    rater: Optional[UserRead] = None
    ratee: Optional[UserRead] = None
    
    class Config:
        from_attributes = True
