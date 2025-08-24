from fastapi import HTTPException, status
from app.db.fake_db import jobs_db
from app.schemas.job_schema import JobResponse, JobBase
from typing import List

async def get_all_jobs_service(
        min_salary: int | None = None,
        max_salary: int | None = None,
        location: str | None = None,
        skill: str | None = None
) -> List[JobResponse]:
    results = jobs_db

    if min_salary is not None:
        results = [job for job in results if job.salary >= min_salary]

    if max_salary is not None:
        results = [job for job in results if job.salary <= max_salary]

    if location is not None:
        results = [job for job in results if job.location.lower() == location.lower()]

    if skill is not None:
        results = [job for job in results if skill.lower() in job.skill.lower()]

    return results


async def get_job_service(job_id: int) -> JobResponse:
    job = next((job for job in jobs_db if job.id == job_id), None)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    return job

async def create_job_service(job: JobBase) -> JobResponse:
    new_id = len(jobs_db)+1

    new_job = JobResponse(
        id=new_id,
        title=job.title,
        description=job.description,
        salary=job.salary,
        location=job.location,
        skill=job.skill
    )
    jobs_db.append(new_job)
    return new_job

async def update_job_service(job_id: int, job: JobBase) -> JobResponse:
    index = next((i for i, job in enumerate(jobs_db) if job.id == job_id), None)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    updated_job = JobResponse(
        id = index+1,
        title=job.title,
        description=job.description,
        salary=job.salary,
        location=job.location,
        skill=job.skill
    )
    jobs_db[index] = updated_job
    return updated_job

async def delete_job_service(job_id: int) -> dict:
    job = next((i for i, job in enumerate(jobs_db) if job.id == job_id), None)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    jobs_db.pop(job)
    return {'message': 'Job successfuly deleted!'}




    