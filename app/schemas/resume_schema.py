from pydantic import BaseModel
from typing import List

class ResumeBase(BaseModel):
    title: str
    experience: str
    education: str
    skills: List[str]

class ResumeResponse(ResumeBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
