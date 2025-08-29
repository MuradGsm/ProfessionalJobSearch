from pydantic import BaseModel
from typing import List, Optional

class CategoryBase(BaseModel):
    name: str
    description: str
    is_active: bool = True
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    children: List["CategoryResponse"] = []  # рекурсивно

    class Config:
        from_attributes = True
        orm_mode = True

CategoryResponse.update_forward_refs()

class JobBase(BaseModel):
    title: str
    description: str
    salary: float
    location: str
    employment_type: str
    skills_required: list[str] 


class JobResponse(JobBase):
    id: int
    user_id: int
    category_id: int

    class Config:
        from_attributes = True