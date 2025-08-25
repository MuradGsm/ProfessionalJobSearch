from pydantic import BaseModel
from enum import Enum


class UserRole(str, Enum):
    candidate = 'candidate'
    employer = 'employer'


class UserRequest(BaseModel):
    name: str
    role: UserRole
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    role: UserRole
    email: str
    hashed_password: str
    is_admin: bool = False


class UserLogin(BaseModel):
    email: str
    password: str

