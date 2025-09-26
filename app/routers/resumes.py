from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resumes_model import Resume
from app.models.users_model import User
from app.schemas.resume_schema import ResumeCreate, ResumeResponse, ResumeUpdate
from app.db.database import get_session
from app.auth.deps import get_current_user
from app.services.resumes_service import resume_service
from typing import List

router = APIRouter()


@router.post('/', response_model=ResumeResponse)
async def create_resume(data: ResumeCreate, db: AsyncSession = Depends(get_session), curent_user: User = Depends(get_current_user)):
    return await resume_service.create_resume_service(db,curent_user,data)


@router.put('/{resume_id}', response_model=ResumeResponse)
async def update_resume(resume_id: int, data: ResumeUpdate, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    return await resume_service.update_resume_service(resume_id, data, db, current_user)

@router.delete('/{resume_id}')
async def delete_resume(resume_id: int, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    return await resume_service.delete_resume_service(resume_id, db, current_user)

@router.patch('/{resume_id}/set-default')
async def set_default_resume(resume_id: int, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    return await resume_service.set_default_resume_service(resume_id, db, current_user)

@router.get('/me', response_model=List[ResumeResponse])
async def get_my_resumes(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    return await resume_service.get_my_resumes_service(db, current_user)