from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import json

from app.database import get_session
from app.api.auth import get_current_user
from app.models.notification import Notification, NotificationStatus, NotificationType, NotificationSettings
from app.models.user import User

router = APIRouter()

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(json.dumps(message))
            except WebSocketDisconnect:
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        disconnected = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.append(user_id)
        
        for user_id in disconnected:
            self.disconnect(user_id)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.get("/", response_model=List[Notification])
async def get_notifications(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取用户通知列表"""
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if status:
        query = query.where(Notification.status == status)
    
    query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
    
    notifications = session.exec(query).all()
    return notifications

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取未读通知数量"""
    query = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.status == NotificationStatus.UNREAD
    )
    
    unread_count = len(session.exec(query).all())
    return {"unread_count": unread_count}

@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """标记通知为已读"""
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此通知")
    
    notification.status = NotificationStatus.READ
    notification.read_at = datetime.utcnow()
    session.add(notification)
    session.commit()
    
    return {"message": "通知已标记为已读"}

@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """标记所有通知为已读"""
    query = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.status == NotificationStatus.UNREAD
    )
    
    unread_notifications = session.exec(query).all()
    for notification in unread_notifications:
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.utcnow()
        session.add(notification)
    
    session.commit()
    return {"message": f"已标记 {len(unread_notifications)} 条通知为已读"}

@router.get("/settings")
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取用户通知设置"""
    settings = session.exec(
        select(NotificationSettings).where(NotificationSettings.user_id == current_user.id)
    ).first()
    
    if not settings:
        # 如果用户没有设置，创建默认设置
        settings = NotificationSettings(user_id=current_user.id)
        session.add(settings)
        session.commit()
        session.refresh(settings)
    
    return settings

@router.put("/settings")
async def update_notification_settings(
    settings_data: dict,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """更新用户通知设置"""
    settings = session.exec(
        select(NotificationSettings).where(NotificationSettings.user_id == current_user.id)
    ).first()
    
    if not settings:
        settings = NotificationSettings(user_id=current_user.id)
    
    # 更新设置字段
    for key, value in settings_data.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    settings.updated_at = datetime.utcnow()
    session.add(settings)
    session.commit()
    session.refresh(settings)
    
    return settings

# 通知创建工具函数
async def create_notification(
    session: Session,
    user_id: int,
    title: str,
    content: str,
    notification_type: NotificationType,
    related_post_id: Optional[int] = None,
    related_claim_id: Optional[int] = None,
    related_comment_id: Optional[int] = None,
    extra_data: Optional[dict] = None
):
    """创建通知并发送实时推送"""
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        type=notification_type,
        related_post_id=related_post_id,
        related_claim_id=related_claim_id,
        related_comment_id=related_comment_id,
        extra_data=extra_data
    )
    
    session.add(notification)
    session.commit()
    session.refresh(notification)
    
    # 通过WebSocket发送实时通知
    await manager.send_personal_message({
        "type": "notification",
        "data": {
            "id": notification.id,
            "title": notification.title,
            "content": notification.content,
            "type": notification.type,
            "created_at": notification.created_at.isoformat()
        }
    }, user_id)
    
    return notification