from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Float, ARRAY, Index, Enum as SQLEnum, CheckConstraint, text
from datetime import datetime, timedelta
from typing import Optional
from app.schemas.job_schema import EducationLevel, SkillLevel, EmploymentType

class Categories(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    
    # Relationships
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="category", lazy='select')
    children: Mapped[list["Categories"]] = relationship(
        "Categories", backref="parent", remote_side="Categories.id"
    )

    __table_args__ = (
        Index('idx_category_name', 'name'),
        Index('idx_category_active', 'is_active'),
        Index('idx_category_parent', 'parent_id'),
        Index('idx_category_active_parent', 'is_active', 'parent_id'),
        CheckConstraint('parent_id != id', name='check_no_self_reference'),
    )

    def has_cycle(self) -> bool:
        """Check if adding parent_id would create a cycle"""
        if not self.parent_id:
            return False
        
        visited = set()
        current = self.parent
        
        while current:
            if current.id in visited or current.id == self.id:
                return True
            visited.add(current.id)
            current = current.parent
        
        return False

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"

class Job(Base):
    id: Mapped[pk_int]
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    employment_type: Mapped[EmploymentType] = mapped_column(SQLEnum(EmploymentType), nullable=False)
    education_level: Mapped[Optional[EducationLevel]] = mapped_column(SQLEnum(EducationLevel), nullable=True)
    skill_levels: Mapped[list[SkillLevel]] = mapped_column(ARRAY(SQLEnum(SkillLevel)), nullable=False)
    skills_required: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True, default=[])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)

    # Relationships
    category: Mapped["Categories"] = relationship("Categories", back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="job", cascade="all, delete-orphan", lazy='select'
    )
    company: Mapped["Company"] = relationship("Company", back_populates="jobs")

    __table_args__ = (
        Index('idx_job_category', 'category_id'),
        Index('idx_job_company', 'company_id'),
        Index('idx_job_location', 'location'),
        Index('idx_job_active_expires', 'is_active', 'expires_at'),
        Index('idx_job_salary', 'salary'),
        Index('idx_job_employment_type', 'employment_type'),
        Index('idx_job_education_level', 'education_level'),
        Index('idx_job_skill_levels', 'skill_levels', postgresql_using='gin'),
        Index('idx_job_skills_required', 'skills_required', postgresql_using='gin'),
        Index('idx_job_tags', 'tags', postgresql_using='gin'),
        Index('idx_job_salary_location', 'salary', 'location'),
        Index('idx_job_active_company_expires', 'is_active', 'company_id', 'expires_at'),
        Index('idx_job_active_category_salary', 'is_active', 'category_id', 'salary'),
        Index('idx_job_employment_education', 'employment_type', 'education_level'),
        Index('idx_job_company_active', 'company_id', 'is_active'),
        CheckConstraint('salary > 0', name='check_positive_salary'),
        CheckConstraint('expires_at > created_at', name='check_future_expiry'),
        CheckConstraint('array_length(skill_levels, 1) <= 2', name='check_max_skill_levels'),
        CheckConstraint('array_length(skill_levels, 1) >= 1', name='check_min_skill_levels'),
        CheckConstraint('array_length(tags, 1) <= 10 OR tags IS NULL', name='check_max_tags'),
    )

    # --- Чистая бизнес-логика без session ---
    def is_expired(self, current_time: datetime = None) -> bool:
        current_time = current_time or datetime.utcnow()
        return current_time > self.expires_at

    def days_until_expiry(self, current_time: datetime = None) -> int:
        current_time = current_time or datetime.utcnow()
        if self.is_expired(current_time):
            return 0
        return (self.expires_at - current_time).days

    def hours_until_expiry(self, current_time: datetime = None) -> int:
        current_time = current_time or datetime.utcnow()
        if self.is_expired(current_time):
            return 0
        delta = self.expires_at - current_time
        return int(delta.total_seconds() // 3600)

    def auto_deactivate_if_expired(self, current_time: datetime = None) -> bool:
        if self.is_expired(current_time) and self.is_active:
            self.is_active = False
            return True
        return False

    def matches_candidate_skills(self, candidate_skills: list[str], threshold: float = 0.5) -> bool:
        if not candidate_skills or not self.skills_required:
            return False
        candidate_set = {s.lower() for s in candidate_skills}
        required_set = {s.lower() for s in self.skills_required}
        matches = len(candidate_set & required_set)
        return matches / len(required_set) >= threshold

    def add_tag(self, tag: str) -> bool:
        if not tag or not tag.strip():
            return False
        tag = tag.strip().lower()
        if not self.tags:
            self.tags = []
        if tag not in self.tags and len(self.tags) < 10:
            self.tags.append(tag)
            return True
        return False

    def remove_tag(self, tag: str) -> bool:
        if not self.tags or not tag:
            return False
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', location='{self.location}', employment_type='{self.employment_type.value}')>"
