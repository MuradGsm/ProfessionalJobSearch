from pydantic import BaseModel, Field, ConfigDict
from typing import List

class ResumeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    experience: str = Field(..., min_length=5)
    skills: List[str] = Field(..., min_length=1)  
    is_default: bool = False
    is_public: bool = True

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)