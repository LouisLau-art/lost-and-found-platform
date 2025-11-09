from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .rating import RatingRead

class RatingStats(BaseModel):
    """用户评价统计信息"""
    total_count: int
    average_score: float
    five_star_count: int
    four_star_count: int
    three_star_count: int
    two_star_count: int
    one_star_count: int
    positive_percentage: float  # 好评率(4-5星)

class UserRatingSummary(BaseModel):
    """用户评价汇总信息"""
    user_id: int
    stats: RatingStats
    recent_ratings: List[RatingRead]
    
    class Config:
        from_attributes = True