from fastapi import HTTPException, status, Query
from app.schemas.user_schema import UserResponse
from app.schemas.resume_schema import ResumeResponse
from app.db.fake_db import users_db, resumes_db
from typing import List, Optional

async def get_all_users_service() -> List[UserResponse]:
    return users_db

async def get_user_service(user_id:int) -> UserResponse:
    user = next((user for user in users_db if user.id == user_id),None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


async def search_candidates_service(skill: Optional[str] = None) -> List[ResumeResponse]:
    if skill:
        results = []
        for resume in resumes_db:
            skills_list = [s.strip().lower() for s in resume.skills.split(",")]
            if skill.lower() in skills_list:
                results.append(resume)
        return results
    return resumes_db
