from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.services.application_service import (
    get_all_applications_service,
    add_application_service,
    update_application_service,
    delete_application_service
)
from app.utils.required import candidate_required
from typing import List
from app.schemas.application_schema import ApplicationResponse, ApplicationBase
from app.schemas.user_schema import UserResponse


router = APIRouter(prefix='/aplications', tags=['aplications'])

@router.get('/', response_model=List[ApplicationResponse])
async def get_all_aplications(current_user: UserResponse = Depends(candidate_required), session: AsyncSession = Depends(get_session)):
    return await get_all_applications_service(current_user, session)

@router.post('/', response_model=ApplicationResponse)
async def add_aplication(
    status: str,
    job_id: int, 
    current_user: UserResponse = Depends(candidate_required), 
    session: AsyncSession = Depends(get_session)
    ):
    return await add_application_service(session, job_id, current_user, status)

@router.put('/{aplication_id}', response_model=ApplicationResponse)
async def update_aplication(aplication_id: int,
                             status: str, 
                             current_user: UserResponse = Depends(candidate_required),
                             session: AsyncSession = Depends(get_session)):
    return await update_application_service(aplication_id, status, current_user, session)

@router.delete('/{aplication_id}')
async def delete_application(aplication_id: int, current_user: UserResponse = Depends(candidate_required), session: AsyncSession = Depends(get_session)):
    return await delete_application_service(aplication_id, current_user, session)