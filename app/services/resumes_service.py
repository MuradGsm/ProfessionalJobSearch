from fastapi import HTTPException, status
from app.db.fake_db import resumes_db, users_db
from app.schemas.resume_schema import ResumeBase, ResumeResponse
from app.schemas.user_schema import UserResponse
from typing import List


async def get_all_resumes_service(current_user: UserResponse) -> List[ResumeResponse]:
    results = []
    for resume in resumes_db:
        if current_user.role == 'employer' or resume.user_id == current_user.id:
            results.append(resume)
    return results

async def get_resume_service(resume_id: int, current_user: UserResponse) -> ResumeResponse:
    resume = next((r for r in resumes_db if r.id == resume_id), None)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    if resume.user_id == current_user.id or current_user.role == 'employer':
        return resume
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to edit this resume')

async def create_resume_service(resume: ResumeBase, current_user: UserResponse) -> ResumeResponse:
    new_id  = len(resumes_db)+1
    new_resume = ResumeResponse(
        id= new_id,
        user_id=current_user.id,
        title=resume.title,
        expirence=resume.expirence,
        education=resume.education,
        skills=resume.skills
    )
    resumes_db.append(new_resume)
    return new_resume

async def update_resume_service(resume_id: int,resume: ResumeBase, current_user: UserResponse) -> ResumeResponse:
    index = next((i for i,resume in enumerate(resumes_db) if resume.id == resume_id), None)
    if index is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    old_resume = resumes_db[index]
    if old_resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to edit this resume')
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

async def delete_resume_service(resume_id: int, current_user: UserResponse) -> dict:
    resume_index = next((i for i,resume in enumerate(resumes_db) if resume.id == resume_id), None)
    if resume_index is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    if resumes_db[resume_index].user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to edit this resume')
    resumes_db.pop(resume_index)
    return {'message': 'Resume deleted successfully'}