from sqlmodel import Session
from typing import Optional
from app.models.notification import Notification, NotificationType, NotificationSettings
from app.models.user import User
from app.models.post import Post
from app.models.claim import Claim
from app.models.comment import Comment
from app.api.notifications import create_notification

class NotificationService:
    """通知服务类"""
    
    @staticmethod
    async def create_claim_notification(
        session: Session,
        claim: Claim,
        post: Post
    ):
        """创建认领通知"""
        # 给帖子作者发送认领通知
        title = "新的认领请求"
        content = f"用户 {claim.claimer.name} 对您的帖子《{post.title}》提交了认领请求"
        
        await create_notification(
            session=session,
            user_id=post.author_id,
            title=title,
            content=content,
            notification_type=NotificationType.CLAIM_CREATED,
            related_post_id=post.id,
            related_claim_id=claim.id,
            extra_data={
                "claimer_name": claim.claimer.name,
                "post_title": post.title,
                "claim_message": claim.message
            }
        )
    
    @staticmethod
    async def create_claim_approved_notification(
        session: Session,
        claim: Claim,
        post: Post
    ):
        """创建认领批准通知"""
        # 给认领者发送批准通知
        title = "认领请求已批准"
        content = f"您的认领请求《{post.title}》已被批准"
        
        await create_notification(
            session=session,
            user_id=claim.claimer_id,
            title=title,
            content=content,
            notification_type=NotificationType.CLAIM_APPROVED,
            related_post_id=post.id,
            related_claim_id=claim.id,
            extra_data={
                "post_title": post.title,
                "approver_name": post.author.name
            }
        )
    
    @staticmethod
    async def create_claim_rejected_notification(
        session: Session,
        claim: Claim,
        post: Post
    ):
        """创建认领拒绝通知"""
        # 给认领者发送拒绝通知
        title = "认领请求已拒绝"
        content = f"您的认领请求《{post.title}》已被拒绝"
        
        await create_notification(
            session=session,
            user_id=claim.claimer_id,
            title=title,
            content=content,
            notification_type=NotificationType.CLAIM_REJECTED,
            related_post_id=post.id,
            related_claim_id=claim.id,
            extra_data={
                "post_title": post.title,
                "rejecter_name": post.author.name
            }
        )
    
    @staticmethod
    async def create_comment_notification(
        session: Session,
        comment: Comment,
        post: Post
    ):
        """创建评论通知"""
        # 给帖子作者发送评论通知（排除作者自己评论）
        if comment.author_id != post.author_id:
            title = "新的评论"
            content = f"用户 {comment.author.name} 评论了您的帖子《{post.title}》"
            
            await create_notification(
                session=session,
                user_id=post.author_id,
                title=title,
                content=content,
                notification_type=NotificationType.NEW_COMMENT,
                related_post_id=post.id,
                related_comment_id=comment.id,
                extra_data={
                    "commenter_name": comment.author.name,
                    "post_title": post.title,
                    "comment_content": comment.content[:100]  # 截取前100字符
                }
            )
    
    @staticmethod
    async def create_system_notification(
        session: Session,
        user_id: int,
        title: str,
        content: str,
        extra_data: Optional[dict] = None
    ):
        """创建系统通知"""
        await create_notification(
            session=session,
            user_id=user_id,
            title=title,
            content=content,
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            extra_data=extra_data
        )
    
    @staticmethod
    def should_send_notification(
        session: Session,
        user_id: int,
        notification_type: NotificationType
    ) -> bool:
        """检查是否应该发送通知"""
        settings = session.exec(
            select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        ).first()
        
        if not settings:
            return True  # 如果没有设置，默认发送
        
        # 检查免打扰模式
        if settings.do_not_disturb:
            current_hour = datetime.utcnow().hour
            if (settings.quiet_hours_start is not None and 
                settings.quiet_hours_end is not None):
                if settings.quiet_hours_start <= current_hour <= settings.quiet_hours_end:
                    return False
        
        # 检查具体通知类型设置
        if notification_type == NotificationType.CLAIM_CREATED:
            return settings.claim_notifications
        elif notification_type == NotificationType.CLAIM_APPROVED:
            return settings.claim_notifications
        elif notification_type == NotificationType.CLAIM_REJECTED:
            return settings.claim_notifications
        elif notification_type == NotificationType.NEW_COMMENT:
            return settings.comment_notifications
        elif notification_type == NotificationType.SYSTEM_ANNOUNCEMENT:
            return settings.system_notifications
        
        return True

# 导入select和datetime
from sqlmodel import select
from datetime import datetime