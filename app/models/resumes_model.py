from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ARRAY, ForeignKey, Boolean, Index, UniqueConstraint
from typing import Optional
from datetime import datetime

class Resume(Base):
    id: Mapped[pk_int]
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    experience: Mapped[str] = mapped_column(String, nullable=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    version: Mapped[int] = mapped_column(default=1)

    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    summary: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    education: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    certifications: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])

    views: Mapped[list["ResumeView"]] = relationship("ResumeView", back_populates="resume")
    view_count: Mapped[int] = mapped_column(default=0)
    download_count: Mapped[int] = mapped_column(default=0)

    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")

    __table_args__ = (
        Index('idx_resume_user', 'user_id'),
        Index('idx_resume_public', 'is_public'),
        Index('idx_resume_default', 'is_default'),
        Index('idx_resume_slug', 'slug'),
        Index('idx_resume_version', 'user_id', 'version'),
        Index('idx_resume_skills', 'skills', postgresql_using='gin'),
        Index('idx_resume_languages', 'languages', postgresql_using='gin'),
        Index('idx_resume_deleted', 'deleted_at'),
        UniqueConstraint('user_id', 'is_default', name='uq_user_default_resume'),
    )

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, title={self.title}, user_id={self.user_id})>"

class ResumeView(Base):
    id: Mapped[pk_int]
    resume: Mapped["Resume"] = relationship("Resume", back_populates="views")
    viewer: Mapped["User"] = relationship("User", back_populates="resume_views")
    