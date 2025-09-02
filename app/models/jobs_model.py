from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Float, ARRAY, Index, Enum as SQLEnum, CheckConstraint, text
from datetime import datetime
from typing import Optional
from app.schemas.job_schema import EducationLevel, SkillLevel, EmploymentType

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
        CheckConstraint('parent_id != id', name='check_no_self_reference'),
    )

    @property
    def active_jobs_count(self) -> int:
        """Count of active jobs in this category"""
        return len([job for job in self.jobs if job.is_active and not job.is_expired])

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
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    # Relationships
    category: Mapped["Categories"] = relationship("Categories", back_populates="jobs")
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        # Basic indexes
        Index('idx_job_category', 'category_id'),
        Index('idx_job_user', 'user_id'),
        Index('idx_job_location', 'location'),
        Index('idx_job_active_expires', 'is_active', 'expires_at'),
        Index('idx_job_salary', 'salary'),
        Index('idx_job_employment_type', 'employment_type'),
        Index('idx_job_education_level', 'education_level'),
        
        # GIN indexes for arrays (PostgreSQL specific)
        Index('idx_job_skill_levels', 'skill_levels', postgresql_using='gin'),
        Index('idx_job_skills_required', 'skills_required', postgresql_using='gin'),
        Index('idx_job_tags', 'tags', postgresql_using='gin'),
        
        # Composite indexes for popular searches
        Index('idx_job_salary_location', 'salary', 'location'),
        Index('idx_job_active_category_salary', 'is_active', 'category_id', 'salary'),
        Index('idx_job_employment_education', 'employment_type', 'education_level'),
        
        # Business constraints
        CheckConstraint('salary > 0', name='check_positive_salary'),
        CheckConstraint('expires_at > created_at', name='check_future_expiry'),
        CheckConstraint('array_length(skill_levels, 1) <= 2', name='check_max_skill_levels'),
        CheckConstraint('array_length(skill_levels, 1) >= 1', name='check_min_skill_levels'),
        CheckConstraint('array_length(tags, 1) <= 10 OR tags IS NULL', name='check_max_tags'),
    )

    @property
    def is_expired(self) -> bool:
        """Check if job has expired"""
        return datetime.utcnow() > self.expires_at

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until expiry"""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return delta.days

    @property
    def hours_until_expiry(self) -> int:
        """Calculate hours until expiry for more precise tracking"""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return int(delta.total_seconds() // 3600)

    def auto_deactivate_if_expired(self) -> bool:
        """Automatically deactivate job if expired"""
        if self.is_expired and self.is_active:
            self.is_active = False
            return True
        return False

    def matches_candidate_skills(self, candidate_skills: list[str]) -> bool:
        """Check if candidate skills match required skills"""
        if not candidate_skills:
            return False
        
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        required_skills_lower = [skill.lower() for skill in self.skills_required]
        
        # Check if at least 50% of required skills are covered
        matches = sum(1 for skill in required_skills_lower if skill in candidate_skills_lower)
        return matches >= len(self.skills_required) * 0.5

    def get_skill_levels_count(self) -> int:
        """Get count of skill levels"""
        return len(self.skill_levels) if self.skill_levels else 0

    def has_skill_level(self, skill_level: SkillLevel) -> bool:
        """Check if job requires specific skill level"""
        return skill_level in (self.skill_levels or [])

    def add_tag(self, tag: str) -> bool:
        """Add tag if not exists and within limit"""
        if not self.tags:
            self.tags = []
        
        if tag.strip() and tag not in self.tags and len(self.tags) < 10:
            self.tags.append(tag.strip())
            return True
        return False

    def remove_tag(self, tag: str) -> bool:
        """Remove tag if exists"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    @classmethod
    def get_expiring_soon(cls, session, days: int = 7):
        """Get jobs expiring within specified days"""
        from sqlalchemy import select, and_
        
        cutoff_date = datetime.utcnow() + datetime.timedelta(days=days)
        return session.execute(
            select(cls).where(
                and_(
                    cls.is_active == True,
                    cls.expires_at <= cutoff_date,
                    cls.expires_at > datetime.utcnow()
                )
            )
        ).scalars().all()

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', location='{self.location}', employment_type='{self.employment_type.value}')>"