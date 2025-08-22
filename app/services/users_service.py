from fastapi import HTTPException, status
from app.schemas.user_schema import UserResponse, UserBase
from app.db.fake_db import users_db
from typing import List

async def get_all_users_service() -> List[UserResponse]:
    return users_db

async def get_user_service(user_id:int) -> UserResponse:
    user = next((user for user in users_db if user.id == user_id),None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

async def create_user_service(user: UserBase) -> UserResponse:
    new_id = len(users_db) + 1

    new_user = UserResponse(
        id = new_id,
        name = user.name, 
        role= user.role
    )
    users_db.append(new_user)
    return new_user