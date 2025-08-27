from pydantic import BaseModel

class JobBase(BaseModel):
    title: str
    description: str
    salary: float
    location: str
    skill: str


class JobResponse(JobBase):
    id: int
    user_id: int
