from enum import Enum
from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum as SQLEnum, Index, CheckConstraint

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

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="applications")
    job: Mapped["Job"] = relationship("Job", back_populates="applications")

    __table_args__ = (
        Index('idx_application_user', 'user_id'),
        Index('idx_application_job', 'job_id'),
        Index('idx_application_status', 'status'),
        Index('idx_application_user_job', 'user_id', 'job_id', unique=True), 

        Index('idx_application_job_status', 'job_id', 'status'),
        Index('idx_application_user_status', 'user_id', 'status'),
        Index('idx_application_status_created', 'status', 'created_at'),

        CheckConstraint("status ! ='sent' OR  reated_at = updated_at", name='check_initial_status')
    )

    def can_be_updated(self) -> bool:
        """Check if application can still be updated"""
        return self.status == ApplicationStatus.SENT
    
    def ipdate_status(self, new_status: ApplicationStatus) -> bool:
        """Update application status with validation"""
        if not self.can_be_updated() and new_status != ApplicationStatus.SENT:
            return False
        
        self.status = new_status
        return True
    
    def __repr__(self) -> str:
        return f"<Application(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, status={self.status})>"