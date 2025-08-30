from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ARRAY, ForeignKey, Boolean, Index

class Resume(Base):
    id: Mapped[pk_int]
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    experience: Mapped[str] = mapped_column(String, nullable=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")

    __table_args__ = (
        Index('idx_resume_user', 'user_id'),
        Index('idx_resume_public', 'is_public'),
        Index('idx_resume_default', 'is_default'),
    )

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, title={self.title}, user_id={self.user_id})>"
