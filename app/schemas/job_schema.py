from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10)
    is_active: bool = True
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    children: List["CategoryResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True

CategoryResponse.model_rebuild() 

class JobBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=50)
    salary: float = Field(..., gt=0)
    location: str = Field(..., min_length=2)
    employment_type: str
    skills_required: List[str] = Field(..., min_items=1)
    expires_at: datetime

    @validator('employment_type')
    def validate_employment_type(cls, v):
        allowed_types = ['full_time', 'part_time', 'contract', 'remote', 'internship']
        if v not in allowed_types:
            raise ValueError('Invalid employment type')
        return v

class JobCreate(JobBase):
    category_id: int

class JobResponse(JobBase):
    id: int
    user_id: int
    category_id: int
    is_active: bool

    class Config:
        from_attributes = True