from fastapi import APIRouter
from app.schemas.resume_schema import ResumeBase, ResumeResponse
from app.services.resumes_service import (
    get_all_resumes_service,
    get_resume_service,
    create_resume_service, 
    update_resume_service,
    delete_resume_service
)
from typing import List

router = APIRouter(prefix='/resumes', tags=['resumes'])

@router.get('/', response_model=List[ResumeResponse])
async def get_all_resumes():
    return await get_all_resumes_service()

@router.get('/{resume_id}', response_model=ResumeResponse)
async def get_resume(resume_id: int):
    return await get_resume_service(resume_id)

@router.post('/', response_model=ResumeResponse)
async def create_resume(resume: ResumeBase, user_id: int):
    return await create_resume_service(resume, user_id)

@router.put('/{resume_id}', response_model=ResumeResponse)
async def update_resume(resume_id: int, resume: ResumeBase):
    return await update_resume_service(resume_id, resume)

@router.delete('/{resume_id}')
async def delete_resume(resume_id: int):
    return await delete_resume_service(resume_id)