from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    candidate = 'candidate'
    employer = 'employer'


class UserRequest(BaseModel):
    name: str
    role: UserRole
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    role: UserRole
    email: EmailStr
    is_admin: bool = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str

