from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Index

class ClaimStatusLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    claim_id: int = Field(foreign_key="claims.id")
    post_id: int = Field(foreign_key="posts.id")
    from_status: str = Field(max_length=20)
    to_status: str = Field(max_length=20)
    actor_user_id: int = Field(foreign_key="users.id")
    actor_role: str = Field(max_length=20)  # owner or claimer
    note: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("ix_claim_status_log_claim_id_created_at", "claim_id", "created_at"),
    )
