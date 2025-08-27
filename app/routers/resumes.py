from fastapi import APIRouter, Depends
from app.schemas.resume_schema import ResumeBase, ResumeResponse
from app.services.resumes_service import (
    get_all_resumes_service,
    get_resume_service,
    create_resume_service, 
    update_resume_service,
    delete_resume_service
)
from app.schemas.user_schema import UserResponse
from app.auth.deps import get_current_user
from app.utils.required import candidate_required
from typing import List

router = APIRouter(prefix='/resumes', tags=['resumes'])

@router.get('/', response_model=List[ResumeResponse])
async def get_all_resumes(current_user: UserResponse = Depends(get_current_user)):
    return await get_all_resumes_service(current_user)

@router.get('/{resume_id}', response_model=ResumeResponse)
async def get_resume(resume_id: int, current_user: UserResponse = Depends(get_current_user)):
    return await get_resume_service(resume_id, current_user)

@router.post('/', response_model=ResumeResponse)
async def create_resume(resume: ResumeBase, current_user: UserResponse = Depends(candidate_required)):
    return await create_resume_service(resume, current_user)

@router.put('/{resume_id}', response_model=ResumeResponse)
async def update_resume(resume_id: int, resume: ResumeBase, current_user: UserResponse = Depends(get_current_user)):
    return await update_resume_service(resume_id, resume, current_user)

@router.delete('/{resume_id}')
async def delete_resume(resume_id: int, current_user: UserResponse = Depends(get_current_user)):
    return await delete_resume_service(resume_id, current_user)