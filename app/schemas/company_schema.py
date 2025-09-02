from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime

class CompanyRole(str, Enum):
    OWNER = 'owner'
    RECRUITER = 'recruiter'
    HR_MANAGER = 'hr'


class CompanyBase(BaseModel):
    name: str 
    description: str
    industry: str
    logo_url: str

class CompanyCreate(CompanyBase):
    owner_id: int


class InviteSchema(BaseModel):
    id:int
    email: EmailStr
    company_role: CompanyRole
    token: str
    expires_at: datetime
    is_used: bool
    company_id: int
    invited_by: int


class CompanyMemberSchema(BaseModel):
    company_role: CompanyRole
    permission: list[str]
    joined_at: datetime
    is_active: bool
    company_id: int
    user_id: int