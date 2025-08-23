from pydantic import BaseModel


class ResumeBase(BaseModel):
    title: str
    expirence: str
    education: str
    skills: str


class ResumeResponse(ResumeBase):
    id: int
    user_id: int