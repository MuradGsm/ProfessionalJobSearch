from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Float, ARRAY, Index
from datetime import datetime
from typing import Optional

class Categories(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    
    # Relationships
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="category")
    children: Mapped[list["Categories"]] = relationship(
        "Categories", backref="parent", remote_side="Categories.id"
    )

    __table_args__ = (
        Index('idx_category_name', 'name'),
        Index('idx_category_active', 'is_active'),
        Index('idx_category_parent', 'parent_id'),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"

class Job(Base):
    id: Mapped[pk_int]
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    skills_required: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    # Relationships
    category: Mapped["Categories"] = relationship("Categories", back_populates="jobs")
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_job_category', 'category_id'),
        Index('idx_job_user', 'user_id'),
        Index('idx_job_location', 'location'),
        Index('idx_job_active_expires', 'is_active', 'expires_at'),
        Index('idx_job_salary', 'salary'),
        Index('idx_job_employment_type', 'employment_type'),
    )

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @property
    def days_until_expiry(self) -> int:
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    def __repr__(self) -> str:
        return f"<Job(title={self.title}, location={self.location}, employment_type={self.employment_type})>"