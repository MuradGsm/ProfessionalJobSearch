from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

# ===== ENUMS =====
class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    REMOTE = "remote"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    HYBRID = "hybrid"

class EducationLevel(str, Enum):
    NO_EDUCATION = "no_education"
    HIGH_SCHOOL = "high_school"
    VOCATIONAL = "vocational"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    CERTIFICATION = "certification"

class SkillLevel(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"

# ===== CATEGORY SCHEMAS =====
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Category name")
    description: str = Field(..., min_length=10, max_length=500, description="Category description")
    is_active: bool = Field(default=True, description="Is category active")
    parent_id: Optional[int] = Field(None, description="Parent category ID for hierarchy")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    children: List["CategoryResponse"] = Field(default_factory=list)
    active_jobs_count: int = Field(description="Count of active jobs in category")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== JOB SCHEMAS =====
class JobBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200, description="Job title")
    description: str = Field(..., min_length=50, description="Detailed job description")
    salary: float = Field(..., gt=0, description="Salary amount")
    location: str = Field(..., min_length=2, max_length=100, description="Job location")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    education_level: Optional[EducationLevel] = Field(None, description="Minimum education level required")
    skill_levels: List[SkillLevel] = Field(..., min_items=1, max_items=2, description="Required skill levels (max 2)")
    skills_required: List[str] = Field(..., min_items=1, description="Required technical skills")
    tags: List[str] = Field(default_factory=list, description="Additional tags for job")
    expires_at: datetime = Field(..., description="Job expiration date")

    @validator('skill_levels')
    def validate_skill_levels(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Skill levels must be unique')
        return v

    @validator('skills_required')
    def validate_skills_required(cls, v):
        # Clean and deduplicate skills
        cleaned_skills = list(set(skill.strip().lower() for skill in v if skill.strip()))
        if not cleaned_skills:
            raise ValueError('At least one technical skill is required')
        if len(cleaned_skills) > 20:
            raise ValueError('Maximum 20 technical skills allowed')
        return cleaned_skills

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Clean, deduplicate and limit tags
            cleaned_tags = list(set(tag.strip().lower() for tag in v if tag.strip()))
            if len(cleaned_tags) > 10:
                raise ValueError('Maximum 10 tags allowed')
            return cleaned_tags
        return []

    @validator('expires_at')
    def validate_expires_at(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Expiration date must be in the future')
        
        # Check if expiry is not too far in future (e.g., max 1 year)
        max_future = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
        if v > max_future:
            raise ValueError('Expiration date cannot be more than 1 year in the future')
        
        return v

    @root_validator
    def validate_business_logic(cls, values):
        employment_type = values.get('employment_type')
        salary = values.get('salary')
        skill_levels = values.get('skill_levels', [])
        
        # Special salary validation for internships
        if employment_type == EmploymentType.INTERNSHIP:
            if salary > 50000:  # Reasonable internship salary limit
                raise ValueError('Internship salary seems too high')
        
        # Validate skill level combinations make sense
        if SkillLevel.INTERN in skill_levels and SkillLevel.SENIOR in skill_levels:
            raise ValueError('Cannot require both INTERN and SENIOR skill levels')
        
        if SkillLevel.INTERN in skill_levels and SkillLevel.LEAD in skill_levels:
            raise ValueError('Cannot require both INTERN and LEAD skill levels')
            
        return values

class JobCreate(JobBase):
    category_id: int = Field(..., description="Category ID for the job")

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=50)
    salary: Optional[float] = Field(None, gt=0)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    employment_type: Optional[EmploymentType] = None
    education_level: Optional[EducationLevel] = None
    skill_levels: Optional[List[SkillLevel]] = Field(None, min_items=1, max_items=2)
    skills_required: Optional[List[str]] = Field(None, min_items=1)
    tags: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None

    @validator('skill_levels')
    def validate_skill_levels(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError('Skill levels must be unique')
        return v

    @validator('expires_at')
    def validate_expires_at(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError('Expiration date must be in the future')
        return v

class JobResponse(JobBase):
    id: int
    company_id: int
    category_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_expired: bool = Field(description="Whether the job has expired")
    days_until_expiry: int = Field(description="Days remaining until expiry")
    hours_until_expiry: int = Field(description="Hours remaining until expiry")

    class Config:
        from_attributes = True

# ===== SEARCH/FILTER SCHEMAS =====
class JobSearchParams(BaseModel):
    # Salary filters
    min_salary: Optional[float] = Field(None, ge=0)
    max_salary: Optional[float] = Field(None, ge=0)
    
    # Location and basic filters
    location: Optional[str] = Field(None, min_length=1)
    employment_type: Optional[EmploymentType] = None
    education_level: Optional[EducationLevel] = None
    skill_level: Optional[SkillLevel] = None
    category_id: Optional[int] = None
    
    # Text search
    skill_search: Optional[str] = Field(None, min_length=1, description="Search in technical skills")
    tag_search: Optional[str] = Field(None, min_length=1, description="Search in tags")
    title_search: Optional[str] = Field(None, min_length=1, description="Search in job titles")
    
    # Status filters
    is_active: Optional[bool] = Field(default=True)
    include_expired: bool = Field(default=False, description="Include expired jobs in results")
    
    # Sorting
    sort_by: Optional[str] = Field(default="created_at", regex="^(created_at|salary|expires_at|title)$")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @validator('max_salary')
    def validate_salary_range(cls, v, values):
        min_salary = values.get('min_salary')
        if min_salary is not None and v is not None and v < min_salary:
            raise ValueError('max_salary must be greater than min_salary')
        return v

# ===== STATISTICS SCHEMAS =====
class JobStats(BaseModel):
    total_jobs: int
    active_jobs: int
    expired_jobs: int
    avg_salary: float
    jobs_by_employment_type: dict
    jobs_by_skill_level: dict
    top_categories: List[dict]
    top_skills: List[dict]

class CategoryStats(BaseModel):
    total_categories: int
    active_categories: int
    categories_with_jobs: int
    avg_jobs_per_category: float

# Rebuild for forward references
CategoryResponse.model_rebuild()