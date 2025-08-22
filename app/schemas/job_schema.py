from pydantic import BaseModel

class JobBase(BaseModel):
    title: str
    description: str
    salary: float
    location: str


class JobResponse(JobBase):
    id: int

