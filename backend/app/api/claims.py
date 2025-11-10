from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
from app.database import get_session
from app.models.user import User
from app.models.claim import Claim
from app.models.post import Post
from app.models.notification import Notification
from app.models.claim_status_log import ClaimStatusLog
from app.schemas.claim import ClaimCreate, ClaimRead, ClaimApprove, ClaimReject
from app.api.auth import get_current_user
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/", response_model=ClaimRead)
async def create_claim(
    claim: ClaimCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """创建认领请求"""
    # 检查帖子是否存在
    post = session.get(Post, claim.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 检查是否已认领
    if post.is_claimed:
        raise HTTPException(status_code=400, detail="Post already claimed")
    
    # 不能认领自己的帖子
    if post.author_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot claim your own post")
    
    # 检查是否已经提交过认领请求
    existing = session.exec(
        select(Claim).where(
            Claim.post_id == claim.post_id,
            Claim.claimer_id == current_user.id,
            Claim.status.in_(["pending", "approved"])
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already have a pending or approved claim")
    
    # 创建认领请求
    db_claim = Claim(
        post_id=claim.post_id,
        claimer_id=current_user.id,
        message=claim.message
    )
    session.add(db_claim)
    session.commit()
    session.refresh(db_claim)
    
    # 发送通知给帖子作者
    await NotificationService.create_claim_notification(session, db_claim, post)
    
    # Reload with relationships for nested serialization
    created = session.exec(
        select(Claim)
        .options(selectinload(Claim.post), selectinload(Claim.claimer))
        .where(Claim.id == db_claim.id)
    ).first()
    return created

@router.get("/my-claims", response_model=List[ClaimRead])
def get_my_claims(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取我提交的认领请求"""
    claims = session.exec(
        select(Claim)
        .options(selectinload(Claim.post), selectinload(Claim.claimer))
        .where(Claim.claimer_id == current_user.id)
        .order_by(Claim.created_at.desc())
    ).all()
    return claims

@router.get("/post/{post_id}", response_model=List[ClaimRead])
def get_post_claims(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取某个帖子的所有认领请求（仅帖子作者可见）"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only post owner can view claims")
    
    claims = session.exec(
        select(Claim)
        .options(selectinload(Claim.post), selectinload(Claim.claimer))
        .where(Claim.post_id == post_id)
        .order_by(Claim.created_at.desc())
    ).all()
    return claims

@router.post("/{claim_id}/approve", response_model=ClaimRead)
async def approve_claim(
    claim_id: int,
    approve: ClaimApprove,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """确认认领（仅帖子作者可操作）。使用事务保证状态更新的原子性。"""
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    post = session.get(Post, claim.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only post owner can approve claims")

    if claim.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending claims can be approved")

    if post.is_claimed:
        raise HTTPException(status_code=409, detail="Post already claimed")

    try:
        with session.begin():
            prev_status = claim.status
            claim.status = "approved"
            claim.owner_reply = approve.owner_reply
            claim.confirmed_at = datetime.utcnow()
            claim.updated_at = datetime.utcnow()

            post.is_claimed = True
            post.status = "resolved"  # 更新帖子状态为已解决
            post.updated_at = datetime.utcnow()

            session.add(claim)
            session.add(post)

            log = ClaimStatusLog(
                claim_id=claim.id,
                post_id=post.id,
                from_status=prev_status,
                to_status=claim.status,
                actor_user_id=current_user.id,
                actor_role="owner",
                note=approve.owner_reply
            )
            session.add(log)
    except Exception:
        # 事务会自动回滚，抛出通用错误
        raise HTTPException(status_code=500, detail="Failed to approve claim due to server error")

    session.refresh(claim)

    # 发送通知给认领者（事务提交后）
    await NotificationService.create_claim_approved_notification(session, claim, post)

    # Return with relationships loaded
    approved = session.exec(
        select(Claim)
        .options(selectinload(Claim.post), selectinload(Claim.claimer))
        .where(Claim.id == claim.id)
    ).first()
    return approved

@router.post("/{claim_id}/reject", response_model=ClaimRead)
async def reject_claim(
    claim_id: int,
    reject: ClaimReject,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """拒绝认领（仅帖子作者可操作）。使用事务保证状态更新的原子性。"""
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    post = session.get(Post, claim.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only post owner can reject claims")

    if claim.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending claims can be rejected")

    try:
        with session.begin():
            prev_status = claim.status
            claim.status = "rejected"
            claim.owner_reply = reject.owner_reply
            claim.updated_at = datetime.utcnow()
            session.add(claim)

            log = ClaimStatusLog(
                claim_id=claim.id,
                post_id=post.id,
                from_status=prev_status,
                to_status=claim.status,
                actor_user_id=current_user.id,
                actor_role="owner",
                note=reject.owner_reply
            )
            session.add(log)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to reject claim due to server error")

    session.refresh(claim)

    await NotificationService.create_claim_rejected_notification(session, claim, post)

    rejected = session.exec(
        select(Claim)
        .options(selectinload(Claim.post), selectinload(Claim.claimer))
        .where(Claim.id == claim.id)
    ).first()
    return rejected

@router.delete("/{claim_id}")
def cancel_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """取消认领请求（仅认领者可操作）。使用事务保证状态更新的原子性。"""
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.claimer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only claimer can cancel")

    if claim.status != "pending":
        raise HTTPException(status_code=400, detail="Can only cancel pending claims")

    try:
        with session.begin():
            prev_status = claim.status
            claim.status = "cancelled"
            claim.updated_at = datetime.utcnow()
            session.add(claim)

            log = ClaimStatusLog(
                claim_id=claim.id,
                post_id=claim.post_id,
                from_status=prev_status,
                to_status=claim.status,
                actor_user_id=current_user.id,
                actor_role="claimer",
                note=None
            )
            session.add(log)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to cancel claim due to server error")

    return {"message": "Claim cancelled successfully"}
