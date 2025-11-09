from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    """通知类型枚举"""
    CLAIM_CREATED = "claim_created"  # 认领请求创建
    CLAIM_APPROVED = "claim_approved"  # 认领请求批准
    CLAIM_REJECTED = "claim_rejected"  # 认领请求拒绝
    CLAIM_CANCELLED = "claim_cancelled"  # 认领请求取消
    NEW_COMMENT = "new_comment"  # 新评论
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # 系统公告
    MESSAGE_RECEIVED = "message_received"  # 收到私信

class NotificationStatus(str, Enum):
    """通知状态枚举"""
    UNREAD = "unread"  # 未读
    READ = "read"  # 已读
    ARCHIVED = "archived"  # 已归档

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    """通知模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 通知基本信息
    title: str = Field(max_length=200)  # 通知标题
    content: str = Field(max_length=1000)  # 通知内容
    type: str = Field(max_length=50)  # 通知类型
    status: str = Field(default=NotificationStatus.UNREAD, max_length=20)  # 通知状态
    
    # 关联数据（用于跳转和详情展示）
    related_post_id: Optional[int] = Field(default=None, foreign_key="posts.id")  # 关联的帖子关联帖子
    related_claim_id: Optional[int] = Field(default=None, foreign_key="claims.id")  # 关联认领
    related_comment_id: Optional[int] = Field(default=None, foreign_key="comments.id")  # 关联评论
    
    # 额外数据（JSON格式存储）
    extra_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # 额外数据
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = Field(default=None)  # 阅读时间
    
    # 外键
    user_id: int = Field(foreign_key="users.id")  # 接收用户
    
    # 关系
    user: Optional["User"] = Relationship(back_populates="notifications")
    related_post: Optional["Post"] = Relationship()
    related_claim: Optional["Claim"] = Relationship()
    related_comment: Optional["Comment"] = Relationship()

class NotificationSettings(SQLModel, table=True):
    """用户通知设置模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 用户ID
    user_id: int = Field(foreign_key="users.id", unique=True)
    
    # 各类通知开关
    email_notifications: bool = Field(default=True)  # 邮件通知
    push_notifications: bool = Field(default=True)  # 推送通知
    
    # 具体通知类型设置
    claim_notifications: bool = Field(default=True)  # 认领相关通知
    comment_notifications: bool = Field(default=True)  # 评论相关通知
    system_notifications: bool = Field(default=True)  # 系统通知
    
    # 免打扰设置
    do_not_disturb: bool = Field(default=False)  # 免打扰模式
    quiet_hours_start: Optional[int] = Field(default=None)  # 免打扰开始时间（小时）
    quiet_hours_end: Optional[int] = Field(default=None)  # 免打扰结束时间（小时）
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # 关系
    user: Optional["User"] = Relationship()

