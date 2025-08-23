from fastapi import HTTPException, status
from app.db.fake_db import resumes_db, users_db
from app.schemas.resume_schema import ResumeBase, ResumeResponse
from typing import List


async def get_all_resumes_service() -> List[ResumeResponse]:
    return resumes_db

async def get_resume_service(resume_id: int) -> ResumeResponse:
    resume = next((r for r in resumes_db if r.id == resume_id), None)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    return resume

async def create_resume_service(resume: ResumeBase, user_id: int) -> ResumeResponse:
    user = next((u for u in users_db if u.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    new_id  = len(resumes_db)+1
    new_resume = ResumeResponse(
        id= new_id,
        user_id=user_id,
        title=resume.title,
        expirence=resume.expirence,
        education=resume.education,
        skills=resume.skills
    )
    resumes_db.append(new_resume)
    return new_resume

async def update_resume_service(resume_id: int,resume: ResumeBase) -> ResumeResponse:
    index = next((i for i,resume in enumerate(resumes_db) if resume.id == resume_id), None)
    if index is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    old_resume = resumes_db[index]
    update_resume = ResumeResponse(
        id = old_resume.id,
        user_id=old_resume.user_id,
        title=resume.title,
        expirence=resume.expirence,
        education=resume.education,
        skills=resume.skills
    )
    resumes_db[index] = update_resume
    return update_resume

async def delete_resume_service(resume_id: int) -> dict:
    resume_index = next((i for i,resume in enumerate(resumes_db) if resume.id == resume_id), None)
    if resume_index is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    resumes_db.pop(resume_index)
    return {'message': 'Resume deleted successfully'}