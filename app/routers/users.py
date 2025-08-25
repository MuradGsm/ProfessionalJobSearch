from fastapi import APIRouter, Query
from app.services.users_service import (get_all_users_service, 
                                        get_user_service, 
                                        search_candidates_service)
from app.schemas.user_schema import UserResponse
from app.schemas.resume_schema import ResumeResponse
from typing import List, Optional

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=List[UserResponse])
async def get_all_users():
    return await get_all_users_service()

@router.get('/search', response_model=List[ResumeResponse])
async def search_candidates(skill: Optional[str] = Query(None)):
    return await search_candidates_service(skill)

@router.get('/{user_id}', response_model=UserResponse)
async def get_user(user_id: int):
    return await get_user_service(user_id)


