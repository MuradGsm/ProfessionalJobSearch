from fastapi import HTTPException, status
from app.db.fake_db import aplications_db, jobs_db, users_db
from app.schemas.aplication_schema import ApplicationBase, ApplicationResponse
from typing import List



async def get_all_aplications_service() -> List[ApplicationResponse]:
    return aplications_db

async def add_aplication_service(job_id: int, user_id: int, status:str ='sent') -> ApplicationResponse:
    user_index = next((i for i,u in enumerate(users_db) if u.id == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Users not found')
    job_index = next((i for i,j in enumerate(jobs_db) if j.id == job_id), None)
    if job_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Jobs not found')
    id = len(aplications_db) + 1
    aplication = ApplicationResponse(
        id=id,
        user_id=users_db[user_index].id,
        job_id=jobs_db[job_index].id,
        status=status
    )
    return aplication

async def update_aplication_service(applicaton_id: int, status: str) -> ApplicationResponse:
    applicaton_index = next((i for i,a in enumerate(aplications_db) if a.id == applicaton_id), None)
    if applicaton_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Users not found')
    old_aplicaton = aplications_db[applicaton_index]
    update_aplication = ApplicationResponse(
        id=applicaton_id,
        job_id=old_aplicaton.job_id,
        user_id = old_aplicaton.user_id,
        status = status
    )
    aplications_db[applicaton_index] = update_aplication
    return update_aplication


