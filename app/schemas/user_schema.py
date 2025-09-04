from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    candidate = 'candidate'
    employer = 'employer'


class UserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = Field(..., description="Choose role", example="candidate")
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    role: UserRole 
    email: EmailStr
    is_admin: bool = False
    is_active: bool = True
    company_id: Optional[int] = None

    class Config:
        from_attributes = True 


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"