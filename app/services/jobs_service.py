from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.jobs_model import Job
from app.schemas.job_schema import JobBase
from app.schemas.user_schema import UserResponse
from typing import List, Optional
from datetime import datetime, timedelta

async def get_all_jobs_service(
        session: AsyncSession,
        min_salary: Optional[int] = None,
        max_salary: Optional[int] = None,
        location: Optional[str] = None,
        skill: Optional[str] = None,
) -> List[Job]:
    query = select(Job)
    if min_salary is not None:
        query = query.where(Job.salary >= min_salary)

    if max_salary is not None:
        query = query.where(Job.salary <= max_salary)

    if location is not None:
        query = query.where(Job.location.ilike(f"%{location}%"))

    if skill is not None:
        query = query.where(Job.skills_required.any(skill))

    results = await session.execute(query)
    job = results.scalars().all()

    return job


async def get_job_service(job_id: int, session: AsyncSession) -> Job:
    results = await session.execute(select(Job).where(Job.id == job_id))
    job = results.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    return job

async def create_job_service(job: JobBase, current_user: UserResponse, session: AsyncSession) -> Job:
    new_job = Job(
        title=job.title,
        description=job.description,
        salary=job.salary,
        location=job.location,
        employment_type=job.employment_type,
        skills_required=job.skills_required,
        expires_at=job.expires_at,
        category_id=job.category_id,
        user_id=current_user.id
    )
    session.add(new_job)
    await session.commit()
    await session.refresh(new_job)
    return new_job

async def update_job_service(job_id: int, job: JobBase, current_user: UserResponse, session: AsyncSession) -> Job:
    results = await session.execute(select(Job).where(Job.id == job_id))
    existing_job = results.scalar_one_or_none()
    if existing_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    if existing_job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to edit this job')
    existing_job.title = job.title
    existing_job.description = job.description
    existing_job.salary = job.salary
    existing_job.location = job.location
    existing_job.employment_type = job.employment_type
    existing_job.skills_required = job.skills_required
    existing_job.expires_at = job.expires_at
    existing_job.category_id = job.category_id
    existing_job.user_id = current_user.id
    session.add(existing_job)
    await session.commit()
    await session.refresh(existing_job)
    return existing_job

async def delete_job_service(job_id: int, current_user: UserResponse, session: AsyncSession) -> dict:
    results = await session.execute(select(Job).where(Job.id == job_id))
    job = results.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')
    if job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to delete this job')
    session.delete(job)
    await session.commit()
    return {'message': 'Job successfuly deleted!'}




async def get_expiring_soon(session: AsyncSession, days: int = 7, current_time: datetime = None):
    current_time = current_time or datetime.utcnow()
    cutoff_date = current_time + timedelta(days=days)
    result = await session.execute(
        select(Job).where(
            and_(
                Job.is_active == True,
                Job.expires_at <= cutoff_date,
                Job.expires_at > current_time
            )
        )
    )
    return result.scalars().all()

async def get_active_jobs_count_by_category(session: AsyncSession, category_id: int) -> int:
    result = await session.execute(
        select(func.count(Job.id)).where(
            and_(Job.category_id == category_id, Job.is_active == True, Job.expires_at > func.now())
        )
    )
    return result.scalar_one()