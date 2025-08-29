from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Float, ARRAY
from datetime import datetime
from typing import Optional

# Category
class Categories(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="category")
    children: Mapped[list["Categories"]] = relationship(
        "Categories", backref="parent", remote_side="Categories.id"
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"

# Job
class Job(Base):
    id: Mapped[pk_int]
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    employment_type: Mapped[str] = mapped_column(String, nullable=False)
    skills_required: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    user_id: Mapped[pk_int] = mapped_column(ForeignKey("user.id"), nullable=False)
    category_id: Mapped[pk_int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    category: Mapped["Categories"] = relationship("Categories", back_populates="jobs")

    def __repr__(self) -> str:
        return f"<Job(title={self.title}, location={self.location}, employment_type={self.employment_type})>"
