from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    role: str


class UserResponse(UserBase):
    id: int

