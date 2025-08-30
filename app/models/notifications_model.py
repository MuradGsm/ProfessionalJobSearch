from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum, Index
from enum import Enum

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
    
    # Optional fields for linking to specific entities
    related_id: Mapped[int] = mapped_column(nullable=True)  # Can link to job_id, message_id, etc.
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index('idx_notification_user', 'user_id'),
        Index('idx_notification_unread', 'user_id', 'is_read'),
        Index('idx_notification_type', 'type'),
        Index('idx_notification_created', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"