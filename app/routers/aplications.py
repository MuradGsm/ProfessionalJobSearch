from fastapi import APIRouter
from app.services.aplications_service import (
    get_all_aplications_service,
    add_aplication_service,
    update_aplication_service
)
from typing import List
from app.schemas.aplication_schema import ApplicationResponse, ApplicationBase


router = APIRouter(prefix='/aplications', tags=['aplications'])

@router.get('/', response_model=List[ApplicationResponse])
async def get_all_aplications():
    return await get_all_aplications_service()

@router.post('/', response_model=ApplicationResponse)
async def add_aplication(application: ApplicationBase):
    return await add_aplication_service(application.job_id, application.user_id, application.status)

@router.put('/{aplication_id}', response_model=ApplicationResponse)
async def update_aplication(aplication_id: int, status: str):
    return await update_aplication_service(aplication_id, status)