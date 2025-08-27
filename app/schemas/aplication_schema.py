from pydantic import BaseModel

class ApplicationBase(BaseModel):
    status: str = "sent"  
    job_id: int

class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int