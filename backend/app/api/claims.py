from fastapi import APIRouter, Depends, HTTPException, status
import logging
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

@router.get("/received", response_model=List[ClaimRead])
def get_received_claims(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取我作为帖子作者收到的所有认领请求（聚合所有我的帖子）。"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[RECEIVED_CLAIMS] Current user: {current_user.email} (ID: {current_user.id})")
    
    # 获取当前用户的所有帖子ID
    # 直接使用 .all() 返回整型ID列表，避免元组解包问题
    post_ids = session.exec(
        select(Post.id).where(Post.author_id == current_user.id)
    ).all()
    
    logger.info(f"[RECEIVED_CLAIMS] Found {len(post_ids)} posts for user {current_user.id}: {post_ids}")

    if not post_ids:
        logger.info(f"[RECEIVED_CLAIMS] No posts found, returning empty list")
        return []

    claims = session.exec(
        select(Claim)
        .options(selectinload(Claim.post), selectinload(Claim.claimer))
        .where(Claim.post_id.in_(post_ids))
        .order_by(Claim.created_at.desc())
    ).all()
    
    logger.info(f"[RECEIVED_CLAIMS] Found {len(claims)} claims for user's posts")
    for claim in claims:
        logger.info(f"[RECEIVED_CLAIMS] Claim ID {claim.id}: Post {claim.post_id}, Claimer {claim.claimer_id}, Status {claim.status}")
    
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

    logger = logging.getLogger(__name__)
    logger.info(f"[CLAIM_APPROVE] Approving claim {claim_id} by user {current_user.id}")
    try:
        with session.begin():
            prev_status = claim.status
            claim.status = "approved"
            claim.owner_reply = approve.owner_reply
            claim.confirmed_at = datetime.utcnow()
            claim.updated_at = datetime.utcnow()

            post.is_claimed = True
            # 使用已存在的状态集合: published/draft/deleted；保持published并用is_claimed标识
            # 如果需要展示解决状态，请在前端根据is_claimed渲染。
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
    except Exception as e:
        logger.exception(f"[CLAIM_APPROVE] DB transaction failed for claim {claim_id}: {e}")
        # 事务会自动回滚，抛出通用错误
        raise HTTPException(status_code=500, detail="Failed to approve claim due to server error")

    # 重新加载claim和post，确保关系已就绪（避免懒加载导致的None属性访问）
    claim = session.exec(
        select(Claim)
        .options(selectinload(Claim.post), selectinload(Claim.claimer))
        .where(Claim.id == claim.id)
    ).first()
    post = session.exec(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == claim.post_id)
    ).first()

    # 发送通知给认领者（事务提交后）；通知失败不影响主流程
    try:
        await NotificationService.create_claim_approved_notification(session, claim, post)
    except Exception as e:
        logger.exception(f"[CLAIM_APPROVE] Notification create failed for claim {claim_id}: {e}")

    # Return with relationships loaded（已加载）
    return claim

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
