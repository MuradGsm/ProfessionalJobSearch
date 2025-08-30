from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.resumes_model import Resume
from app.schemas.resume_schema import ResumeBase
from app.schemas.user_schema import UserResponse
from typing import List

async def get_all_resumes_service(current_user: UserResponse, session: AsyncSession) -> List[Resume]:
    if current_user.role == 'employer':
        query = select(Resume)
    else:
        query = select(Resume).where(Resume.user_id == current_user.id)
    results = await session.execute(query)
    return results.scalars().all()

async def get_resume_service(resume_id: int, current_user: UserResponse, session: AsyncSession) -> Resume:
    result = await session.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    if resume.user_id == current_user.id or current_user.role == 'employer':
        return resume
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to access this resume')

async def create_resume_service(resume: ResumeBase, current_user: UserResponse, session: AsyncSession) -> Resume:
    new_resume = Resume(
        user_id=current_user.id,
        title=resume.title,
        experience=resume.experience,
        skills=resume.skills,
        is_public=resume.is_public,
        is_default=resume.is_default
    )
    session.add(new_resume)
    await session.commit()
    await session.refresh(new_resume)
    return new_resume

async def update_resume_service(resume_id: int, resume: ResumeBase, current_user: UserResponse, session: AsyncSession) -> Resume:
    result = await session.execute(select(Resume).where(Resume.id == resume_id))
    resume_existing = result.scalar_one_or_none()
    if resume_existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    if resume_existing.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to edit this resume')

    resume_existing.title = resume.title
    resume_existing.experience = resume.experience
    resume_existing.skills = resume.skills
    resume_existing.is_public = resume.is_public
    resume_existing.is_default = resume.is_default

    session.add(resume_existing)
    await session.commit()
    await session.refresh(resume_existing)
    return resume_existing

async def delete_resume_service(resume_id: int, current_user: UserResponse, session: AsyncSession) -> dict:
    result = await session.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to delete this resume')

    session.delete(resume) 
    await session.commit()
    return {'message': 'Resume deleted successfully'}
