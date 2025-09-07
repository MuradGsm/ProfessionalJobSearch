from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Float, Integer, Index, Enum as SQLEnum, CheckConstraint, Table, Column, ARRAY
from datetime import datetime
from typing import Optional
from app.schemas.job_schema import EducationLevel, SkillLevel, EmploymentType

# Association tables
job_skills = Table(
    'job_skills',
    Base.metadata,
    Column('job_id', ForeignKey('job.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', ForeignKey('skill.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_job_skills_job', 'job_id'),
    Index('idx_job_skills_skill', 'skill_id'),
)

job_tags = Table(
    'job_tags', 
    Base.metadata,
    Column('job_id', ForeignKey('job.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_job_tags_job', 'job_id'),
    Index('idx_job_tags_tag', 'tag_id'),
)

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
        CheckConstraint('parent_id != id', name='check_no_self_reference'),
    )

    def has_cycle(self) -> bool:
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

class Skill(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    normalized_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    jobs: Mapped[list["Job"]] = relationship(
        "Job", 
        secondary=job_skills, 
        back_populates="skills"
    )
    
    __table_args__ = (
        Index('idx_skill_normalized', 'normalized_name'),
        Index('idx_skill_active', 'is_active'),
    )
    
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name.strip()
        self.normalized_name = name.strip().lower()

class Tag(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    normalized_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships  
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        secondary=job_tags,
        back_populates="tags"
    )
    
    __table_args__ = (
        Index('idx_tag_normalized', 'normalized_name'),
        Index('idx_tag_active', 'is_active'),
    )
    
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name.strip()
        self.normalized_name = name.strip().lower()

class Job(Base):
    id: Mapped[pk_int]
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    employment_type: Mapped[EmploymentType] = mapped_column(SQLEnum(EmploymentType), nullable=False)
    education_level: Mapped[Optional[EducationLevel]] = mapped_column(SQLEnum(EducationLevel), nullable=True)
    skill_levels: Mapped[list[SkillLevel]] = mapped_column(ARRAY(SQLEnum(SkillLevel)), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)

    slug: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    meta_title: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)

    view_count: Mapped[int] = mapped_column(default=0)
    applications_count: Mapped[int] = mapped_column(default=0)
    featured_until: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    benefits: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    priority_score: Mapped[int] = mapped_column(default=0)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    deleted_by: Mapped[Optional[int]] =  mapped_column(ForeignKey('user.id'), nullable=True)


    # Relationships
    category: Mapped["Categories"] = relationship("Categories", back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship(
    "Application", 
    back_populates="job", 
    cascade="all, delete-orphan",
    lazy="select",
    order_by="Application.created_at.desc()"
)
    company: Mapped["Company"] = relationship("Company", back_populates="jobs")
    
    skills: Mapped[list["Skill"]] = relationship(
        "Skill",
        secondary=job_skills,
        back_populates="jobs"
    )
    
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", 
        secondary=job_tags,
        back_populates="jobs"
    )

    __table_args__ = (
        Index('idx_job_category', 'category_id'),
        Index('idx_job_company', 'company_id'),
        Index('idx_job_location', 'location'),
        Index('idx_job_active_expires', 'is_active', 'expires_at'),
        Index('idx_job_salary', 'salary'),
        Index('idx_job_employment_type', 'employment_type'),
        Index('idx_job_education_level', 'education_level'),
        Index('idx_job_skill_levels', 'skill_levels', postgresql_using='gin'),
        Index('idx_job_company_active', 'company_id', 'is_active'),
        Index('idx_job_slug', 'slug'),
        Index('idx_job_approved', 'is_approved'),
        Index('idx_job_featured', 'is_featured', 'featured_until'),
        Index('idx_job_priority', 'priority_score'),
        Index('idx_job_deleted', 'deleted_at'),
        Index('idx_job_search', 'title', 'location', postgresql_using='gin'),
        Index('idx_job_location_salary', 'location', 'salary'),
        Index('idx_job_category_featured', 'category_id', 'is_featured', 'priority_score'),
        Index('idx_job_active_approved_featured', 'is_active', 'is_approved', 'is_featured'),

        CheckConstraint('salary > 0', name='check_positive_salary'),
        CheckConstraint('expires_at > created_at', name='check_future_expiry'),
        CheckConstraint('array_length(skill_levels, 1) <= 2', name='check_max_skill_levels'),
        CheckConstraint('array_length(skill_levels, 1) >= 1', name='check_min_skill_levels'),
        CheckConstraint('char_length(trim(title)) > 0', name='check_title_not_empty'),
        CheckConstraint('char_length(trim(description)) >= 50', name='check_description_length'),
        CheckConstraint('expires_at > created_at + interval \'1 day\'', name='check_min_job_duration'),
    )

    # Business logic methods
    def is_expired(self, current_time: datetime = None) -> bool:
        current_time = current_time or datetime.utcnow()
        return current_time > self.expires_at

    def days_until_expiry(self, current_time: datetime = None) -> int:
        current_time = current_time or datetime.utcnow()
        if self.is_expired(current_time):
            return 0
        return (self.expires_at - current_time).days

    def auto_deactivate_if_expired(self, current_time: datetime = None) -> bool:
        if self.is_expired(current_time) and self.is_active:
            self.is_active = False
            return True
        return False

    def matches_candidate_skills(self, candidate_skills: list[str], threshold: float = 0.5) -> bool:
        if not candidate_skills or not self.skills:
            return False
        
        candidate_normalized = {s.lower() for s in candidate_skills}
        required_normalized = {skill.normalized_name for skill in self.skills}
        
        matches = len(candidate_normalized & required_normalized)
        return matches / len(required_normalized) >= threshold
    
    def increment_view_count(self):
        self.view_count += 1

    def is_featured_active(self) -> bool:
        return self.is_featured and (not self.featured_until or self.featured_until > datetime.utcnow())