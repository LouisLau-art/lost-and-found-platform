from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import List
from app.database import get_session
from app.models.user import User
from app.models.claim import Claim
from app.models.rating import Rating
from app.models.post import Post
from app.schemas.rating import RatingCreate, RatingRead
from app.schemas.rating_extended import RatingStats, UserRatingSummary
from app.core.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=RatingRead)
def create_rating(
    rating: RatingCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """创建评价"""
    # 检查认领请求是否存在且已确认
    claim = session.get(Claim, rating.claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.status != "approved":
        raise HTTPException(status_code=400, detail="Can only rate approved claims")
    
    # 检查权限：只能是认领者或帖子作者
    post = session.get(Post, claim.post_id)
    if current_user.id not in [claim.claimer_id, post.author_id]:
        raise HTTPException(status_code=403, detail="Only parties involved can rate")
    
    # 检查是否已经评价过
    existing = session.exec(
        select(Rating).where(
            Rating.claim_id == rating.claim_id,
            Rating.rater_id == current_user.id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already rated this claim")
    
    # 确定被评价者：由系统根据当前用户身份自动推导，避免前端传错
    if current_user.id == claim.claimer_id:
        target_user_id = post.author_id
    elif current_user.id == post.author_id:
        target_user_id = claim.claimer_id
    else:
        # 理论上不会到这里，前面已校验，但为了安全保底
        raise HTTPException(status_code=403, detail="Only parties involved can rate")

    # 创建评价
    db_rating = Rating(
        claim_id=rating.claim_id,
        rater_id=current_user.id,
        ratee_id=target_user_id,
        score=rating.score,
        comment=rating.comment,
        tags=rating.tags
    )
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    
    # 更新被评价者的信用分
    ratee = session.get(User, target_user_id)
    if ratee:
        # 更细化的信用分调整逻辑
        adjustments = {
            5: 8,
            4: 4,
            3: 0,
            2: -3,
            1: -6
        }
        ratee.credit_score += adjustments.get(rating.score, 0)
        session.add(ratee)
        session.commit()
    
    return db_rating

@router.get("/claim/{claim_id}", response_model=List[RatingRead])
def get_claim_ratings(
    claim_id: int,
    session: Session = Depends(get_session)
):
    """获取某个认领请求的所有评价"""
    ratings = session.exec(
        select(Rating).where(Rating.claim_id == claim_id)
    ).all()
    return ratings

@router.get("/user/{user_id}/received", response_model=List[RatingRead])
def get_user_received_ratings(
    user_id: int,
    session: Session = Depends(get_session)
):
    """获取用户收到的评价"""
    ratings = session.exec(
        select(Rating).where(Rating.ratee_id == user_id).order_by(Rating.created_at.desc())
    ).all()
    return ratings

@router.get("/user/{user_id}/stats", response_model=UserRatingSummary)
def get_user_rating_stats(
    user_id: int,
    limit: int = 5,
    session: Session = Depends(get_session)
):
    """获取用户评价统计信息"""
    # 检查用户是否存在
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 获取用户最近的评价
    recent_ratings = session.exec(
        select(Rating).where(Rating.ratee_id == user_id)
        .order_by(Rating.created_at.desc())
        .limit(limit)
    ).all()
    
    # 计算评价统计信息
    total_count = session.exec(
        select(func.count()).where(Rating.ratee_id == user_id)
    ).one()
    
    if total_count == 0:
        # 如果没有评价，返回默认值
        stats = RatingStats(
            total_count=0,
            average_score=0.0,
            five_star_count=0,
            four_star_count=0,
            three_star_count=0,
            two_star_count=0,
            one_star_count=0,
            positive_percentage=0.0
        )
    else:
        # 计算平均分
        avg_score = session.exec(
            select(func.avg(Rating.score)).where(Rating.ratee_id == user_id)
        ).one()
        
        # 计算各星级数量
        five_star = session.exec(
            select(func.count()).where(Rating.ratee_id == user_id, Rating.score == 5)
        ).one()
        
        four_star = session.exec(
            select(func.count()).where(Rating.ratee_id == user_id, Rating.score == 4)
        ).one()
        
        three_star = session.exec(
            select(func.count()).where(Rating.ratee_id == user_id, Rating.score == 3)
        ).one()
        
        two_star = session.exec(
            select(func.count()).where(Rating.ratee_id == user_id, Rating.score == 2)
        ).one()
        
        one_star = session.exec(
            select(func.count()).where(Rating.ratee_id == user_id, Rating.score == 1)
        ).one()
        
        # 计算好评率 (4-5星)
        positive_count = five_star + four_star
        positive_percentage = (positive_count / total_count) * 100 if total_count > 0 else 0
        
        stats = RatingStats(
            total_count=total_count,
            average_score=round(avg_score, 1) if avg_score else 0.0,
            five_star_count=five_star,
            four_star_count=four_star,
            three_star_count=three_star,
            two_star_count=two_star,
            one_star_count=one_star,
            positive_percentage=round(positive_percentage, 1)
        )
    
    return UserRatingSummary(
        user_id=user_id,
        stats=stats,
        recent_ratings=recent_ratings
    )
