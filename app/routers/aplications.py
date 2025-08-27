from fastapi import APIRouter, Depends
from app.services.aplications_service import (
    get_all_aplications_service,
    add_aplication_service,
    update_aplication_service
)
from app.utils.required import candidate_required
from typing import List
from app.schemas.aplication_schema import ApplicationResponse, ApplicationBase
from app.schemas.user_schema import UserResponse


router = APIRouter(prefix='/aplications', tags=['aplications'])

@router.get('/', response_model=List[ApplicationResponse])
async def get_all_aplications(current_user: UserResponse = Depends(candidate_required)):
    return await get_all_aplications_service(current_user)

@router.post('/', response_model=ApplicationResponse)
async def add_aplication(application: ApplicationBase, current_user: UserResponse = Depends(candidate_required)):
    return await add_aplication_service(application.job_id,current_user ,application.status,)

@router.put('/{aplication_id}', response_model=ApplicationResponse)
async def update_aplication(aplication_id: int, status: str, current_user: UserResponse = Depends(candidate_required)):
    return await update_aplication_service(aplication_id, status, current_user)