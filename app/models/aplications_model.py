from enum import Enum
from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum as SQLEnum, Index

class ApplicationStatus(str, Enum):
    SENT = "sent"
    REVIEWED = "reviewed"
    REJECTED = "rejected"

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
        Index('idx_application_user_job', 'user_id', 'job_id', unique=True),  # Prevent duplicate applications
    )

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, status={self.status})>"