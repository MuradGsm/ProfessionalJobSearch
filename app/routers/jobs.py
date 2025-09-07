# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List, Optional

# from app.utils.required import employer_required
# from app.db.database import get_session
# from app.schemas.job_schema import JobResponse, JobBase, CategoryCreate, CategoryResponse
# from app.schemas.user_schema import UserResponse
# from app.services.jobs_service import (
#     get_all_jobs_service, 
#     get_job_service, 
#     create_job_service, update_job_service, 
#     delete_job_service
# )
# from app.services.categories_service import (
#     get_all_categories_service,
#     get_category_service,
#     cretae_category_service,
#     update_category_service,
#     delete_category_service
# )

# router = APIRouter(prefix='/jobs', tags=['jobs'])


# @router.get('/', response_model=List[JobResponse])
# async def get_all_jobs(
#     min_salary: Optional[int] = None,
#     max_salary: Optional[int] = None,
#     location: Optional[str] = None,
#     skill: Optional[str] = None,
#     session: AsyncSession = Depends(get_session)
# ):
#     return await get_all_jobs_service(session, min_salary, max_salary, location, skill)

# @router.get('/{job_id}', response_model=JobResponse)
# async def get_job(job_id: int, session: AsyncSession = Depends(get_session)):
#     return await get_job_service(job_id, session)

# @router.post('/', response_model=JobResponse)
# async def create_job(job: JobBase, current_user: UserResponse = Depends(employer_required), session: AsyncSession = Depends(get_session)):
#     return await create_job_service(job, current_user, session)

# @router.put('/{job_id}', response_model=JobResponse)
# async def update_job(job_id: int, job: JobBase, current_user: UserResponse= Depends(employer_required), session: AsyncSession = Depends(get_session)):
#     return await update_job_service(job_id, job, current_user, session)

# @router.delete('/{job_id}')
# async def delete_job(job_id: int, current_user: UserResponse = Depends(employer_required), session: AsyncSession = Depends(get_session)):
#     return await delete_job_service(job_id, current_user, session)


# @router.get('/categories', response_model=List[CategoryResponse])
# async def get_all_categories(
#     session: AsyncSession = Depends(get_session), 
#     is_active: Optional[bool] = None,
#     parent_id: Optional[int] = None
# ):
#     return await get_all_categories_service(session, is_active, parent_id)

# @router.get('/categories/{id}', response_model=CategoryResponse)
# async def get_category(cat_id: int, session: AsyncSession = Depends(get_session)):
#     return await get_category_service(cat_id, session)

# @router.post('/categories', response_model=CategoryResponse)
# async def cretae_category(cat_data: CategoryCreate, session: AsyncSession):
#     return await cretae_category_service(cat_data, session)

# @router.put('/categories/{id}', response_model=CategoryResponse)
# async def update_category(cat_id: int, cat_db: CategoryCreate, session: AsyncSession = Depends(get_session)):
#     return await update_category_service(cat_id, cat_db, session)

# @router.delete('/categories/{id}')
# async def delete_category(cat_id: int, session: AsyncSession= Depends(get_session)):
#     return await delete_category_service(cat_id, session)