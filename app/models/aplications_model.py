from enum import Enum
from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum, Index, CheckConstraint
from typing import Optional
from datetime import datetime

class ApplicationStatus(str, Enum):
    SENT = "sent"
    REVIEWED = "reviewed"
    REJECTED = "rejected"
    ACCEPTED = "accepted"

class Application(Base):
    id: Mapped[pk_int]
    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(ApplicationStatus, name="applicationstatus"), 
        default=ApplicationStatus.SENT, 
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"))
    reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="applications")
    job: Mapped["Job"] = relationship("Job", back_populates="applications")

    __table_args__ = (
        Index('idx_application_user', 'user_id'),
        Index('idx_application_job', 'job_id'),
        Index('idx_application_status', 'status'),
        Index('idx_application_user_job', 'user_id', 'job_id', unique=True), 
        Index('idx_application_status_reviewed', 'status', 'reviewed_at'),
        Index('idx_application_job_status', 'job_id', 'status'),
        Index('idx_application_user_status', 'user_id', 'status'),
        Index('idx_application_status_created', 'status', 'created_at'),

        CheckConstraint("status != 'sent' OR created_at = updated_at", name='check_initial_status')
    )

    def can_be_updated(self) -> bool:
        """Check if application can still be updated"""
        return self.status == ApplicationStatus.SENT
    
    def update_status(self, new_status: ApplicationStatus) -> bool:
        """Update application status with validation"""
        if not self.can_be_updated() and new_status != ApplicationStatus.SENT:
            return False
        
        self.status = new_status
        return True
    
    def reject(self, reviewer_id: int, reason: str) -> bool:
        """Отклонить заявку"""
        if self.status != ApplicationStatus.SENT:
            return False
        
        self.status = ApplicationStatus.REJECTED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.rejection_reason = reason
        return True

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, status={self.status})>"