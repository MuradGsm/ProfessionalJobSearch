# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.db.database import get_session
# from app.services.users_service import (get_all_users_service, 
#                                         get_user_service)
# from app.schemas.user_schema import UserResponse
# from app.utils.required import admin_required
# from typing import List

# router = APIRouter(prefix='/users', tags=['users'])


# @router.get('/', response_model=List[UserResponse])
# async def get_all_users(
#     session: AsyncSession = Depends(get_session),
#     current_user: UserResponse = Depends(admin_required)
#     ):
#     return await get_all_users_service(session)

# @router.get('/{user_id}', response_model=UserResponse)
# async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
#     return await get_user_service(user_id, session)
