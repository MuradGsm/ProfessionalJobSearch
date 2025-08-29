from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    candidate = 'candidate'
    employer = 'employer'


class UserRequest(BaseModel):
    name: str
    role: UserRole = Field(..., description="Choose role", example="candidate")
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    role: UserRole 
    email: EmailStr
    hashed_password: str
    is_admin: bool = False

    class Config:
        from_attributes = True 


class UserLogin(BaseModel):
    email: EmailStr
    password: str

