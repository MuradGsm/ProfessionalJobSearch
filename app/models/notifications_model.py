from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum, Index, JSON
from enum import Enum
from typing import Optional
from datetime import datetime

class NotificationType(str, Enum):
    message = "message" 
    application = "application"
    job_update = "job_update"
    system = "system"

class Notification(Base):
    id: Mapped[pk_int]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notificationtype"), 
        nullable=False
    )
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    delivery_method: Mapped[str] = mapped_column(String(20), default='in_app')
    group_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    priority: Mapped[str] = mapped_column(String(10), default='normal')
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # ИСПРАВЛЕНО: переименовано metadata -> notification_data
    notification_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    related_id: Mapped[int] = mapped_column(nullable=True)  
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index('idx_notification_user', 'user_id'),
        Index('idx_notification_unread', 'user_id', 'is_read'),
        Index('idx_notification_type', 'type'),
        Index('idx_notification_created', 'created_at'),
        Index('idx_notification_sent', 'is_sent', 'sent_at'),
        Index('idx_notification_priority', "priority"),
        Index('idx_notification_group', 'group_key'),
        Index('idx_notification_expires', 'expires_at'),
        Index('idx_notification_delivery', 'delivery_method'),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"