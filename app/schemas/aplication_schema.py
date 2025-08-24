from pydantic import BaseModel

class ApplicationBase(BaseModel):
    user_id: int
    job_id: int
    status: str = "sent"  

class ApplicationResponse(ApplicationBase):
    id: int
