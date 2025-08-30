from fastapi import HTTPException, status, Query
from app.models.users_model import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

async def get_all_users_service(session: AsyncSession) -> List[User]:
    result = await session.execute(select(User))
    return result.scalars().all()

async def get_user_service(user_id:int, session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.id ==user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

