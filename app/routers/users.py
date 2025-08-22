from fastapi import APIRouter
from app.services.users_service import get_all_users_service, get_user_service, create_user_service
from app.schemas.user_schema import UserResponse, UserBase
from typing import List

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=List[UserResponse])
async def get_all_users():
    return await get_all_users_service()

@router.get('/{user_id}', response_model=UserResponse)
async def get_user(user_id: int):
    return await get_user_service(user_id)

@router.post('/', response_model=UserResponse)
async def create_user(user: UserBase):
    return await create_user_service(user)