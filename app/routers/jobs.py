from fastapi import APIRouter
from app.schemas.job_schema import JobResponse, JobBase
from app.services.jobs_service import get_all_jobs_service, get_job_service, create_job_service, update_job_service, delete_job_service
from typing import List

router = APIRouter(prefix='/jobs', tags=['jobs'])


@router.get('/', response_model=List[JobResponse])
async def get_all_jobs():
    return await get_all_jobs_service()

@router.get('/{job_id}', response_model=JobResponse)
async def get_job(job_id: int):
    return await get_job_service(job_id)

@router.post('/', response_model=JobResponse)
async def create_job(job: JobBase):
    return await create_job_service(job)

@router.put('/{job_id}', response_model=JobResponse)
async def update_job(job_id: int, job: JobBase):
    return await update_job_service(job_id, job)

@router.delete('/{job_id}')
async def delete_job(job_id: int):
    return await delete_job_service(job_id)