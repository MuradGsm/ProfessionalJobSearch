import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from datetime import datetime

from sqlalchemy import select, and_, asc, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload, joinedload

from app.config.cache import CacheMnager
from app.services.categories_service import CategoryService
from app.models.jobs_model import Job, Tag, Skill
from app.models.company_model import Company
from app.schemas.job_schema import JobCreate, JobResponse, JobUpdate, JobSearchParams, SkillLevel
from app.schemas.user_schema import UserResponse
from app.config.exceptions import PermissionDeniedError, BusinessLogicError, ValidationError, EntityNotFoundError
from app.utils.slug import generate_unique_slug
from app.utils.text_processing import clean_and_validate_skills, clean_and_validate_tags


logger = logging.getLogger(__name__)

class JobService:

    def __init__(self, session: AsyncSession, cache_manager: Optional[CacheMnager] = None):
        self.session = session
        self.cache = cache_manager
        self.category_service = CategoryService(session)

    @asynccontextmanager
    async def transaction(self):
        try:
            yield
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f'Transaction rolled back: {str(e)}')
            raise

    async def create_job(self, data: JobCreate, current_user: UserResponse) -> JobResponse:
        logger.info(f"Create job '{data.title}' by user '{current_user.id}' ")

        if current_user.role != 'employer':
            logger.warning(f'Access denied: User {current_user.id} is not an employer')
            raise PermissionDeniedError('Only employers can create jobs')
        
        if not current_user.company_id:
            logger.warning(f"User {current_user.id} has no company assigned")
            raise BusinessLogicError('Employer must be associated with a company')
        
        try:
            async with self.transaction():
                category = await self.category_service.get_category(data.category_id)
                if not category.is_active:
                    raise ValidationError("Cannot create job in inactive category")
                
                await self._validate_user_company_access(current_user)

                skill_objects = await self._process_skills(data.skills_required)

                tag_objects = await self._process_tags(data.tags)

                slug = await self._generate_job_slug(data.title)

                new_job = Job(
                    title = data.title.strip(),
                    description = data.description.strip(),
                    salary = data.salary,
                    location = data.location.strip(),
                    employment_type = data.employment_type,
                    education_level = data.education_level,
                    skill_levels = [level.value for level in data.skill_levels],
                    expires_at = data.expires_at,
                    category_id = category.id,
                    company_id = current_user.company_id,
                    slug = slug,
                    skills = skill_objects,
                    tags = tag_objects,
                    benefits = getattr(data, 'benefits', None),
                    requirements = getattr(data, 'requirements', None)
                )

                self.session.add(new_job)
                await self.session.refresh(
                    new_job, 
                    ['skills', 'tags', 'category', 'company']
                )

                if self.cache:
                    await self._invalidate_job_caches(new_job)

                logger.info(f"Job created successyully: ID {new_job.id}, Title: '{new_job.title}")

                return self._convert_to_response(new_job)
            
        except IntegrityError as e:
            logger.error(f'Database integrity error creating job: {str(e)}')
            raise ValidationError('Job creation failed due to data constraint violation')
        except SQLAlchemyError as e:
            logger.error(f'Database error creating job: {str(e)}')
            raise BusinessLogicError('Job creation failed due to database error')
        except Exception as e:
            logger.error(f'Unexceted error creating job: {str(e)}')
            raise

    async def get_job(self, job_id: int, increment_view: bool =  False) -> JobResponse:
        cache_key = f'job: {job_id}'

        if self.cache and not increment_view:
            cached_job = await self.cache.get(cache_key)
            if cached_job:
                logger.debug(f'Job {job_id} returned from cache')
                return JobResponse.model_validate(cached_job)
        
        try:
            stmt = select(Job).options(
                selectinload(Job.skills),
                selectinload(Job.tags),
                joinedload(Job.category),
                joinedload(Job.company)
            ).where(Job.id == job_id)

            result = await self.session.execute(stmt)
            job = result.scalar_one_or_none()

            if not job:
                logger.warning(f'Job {job_id} not found')
                raise EntityNotFoundError(f'Job with ID {job_id} not found')
            
            if increment_view:
                job.increment_view_count()
                await self.session.commit()
                logger.debug(f'View count incremented for job {job_id}')
            
            job_response = self._convert_to_response(job)

            if self.cache and not increment_view:
                await self.cache.set(cache_key, job_response.model_dump(), expire=3600)
            
            return job_response
        
        except SQLAlchemyError as e:
            logger.error(f'Database error fetching job {job_id}: {str(e)}')
            raise BusinessLogicError('Failed to fetch job')
    
    async def update_job(self, job_id: int, data: JobUpdate, current_user: UserResponse) -> JobResponse:
        logger.info(f"Updating job {job_id} by user {current_user.id}")

        try:
            job = await self._get_job_for_update(job_id, current_user)

            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                if field == 'skills_required' and value is not None:
                    job.skills = await self._process_skills(value)
                elif field == 'tags' and value is not None:
                    job.tags = await self._process_tags(value)
                elif field == 'category_id' and value is not None:
                    category = await self.category_service.get_category(value)
                    if not category.is_active:
                        raise ValidationError('Cannot move job to inactive category')
                    job.category_id = value
                elif field == "skill_levels" and value is not None:
                    job.skill_levels = [level.value for level in value]
                elif hasattr(job, field) and value is not None:
                    setattr(job, field, value)
            
            await self.session.flush()

            await self.session.refresh(job, ['skills', 'tags', 'category', 'company'])

            if self.cache:
                await self._invalidate_job_caches(job)

            logger.info(f'Job {job_id} updated successflly')

            return self._convert_to_response(job)
        
        except SQLAlchemyError as e:
            logger.error(f'Database error updating job {job_id}: {str(e)}')
            raise BusinessLogicError('Failed to update job')
        
    async def search_job(self, params: JobSearchParams) -> Dict[str, Any]:
        logger.debug(f'Searching jobs with params: {params.model_dump()}')

        try:
            stmt = select(Job).options(
                selectinload(Job.skills),
                selectinload(Job.tags),
                joinedload(Job.category),
                joinedload(Job.company)
            )

            conditions = []

            if params.is_active:
                conditions.append(Job.is_active == True)
            
            if not params.include_expired:
                conditions.append(Job.expires_at >= datetime.utcnow())
            
            if params.min_salary is not None:
                conditions.append(Job.salary >= params.min_salary)
            
            if params.max_salary is not None:
                conditions.append(Job.salary <= params.max_salary)
            
            if params.location:
                conditions.append(Job.location.ilike(f"%{params.location}%"))
            
            if params.employment_type:
                conditions.append(Job.employment_type == params.employment_type)
            
            if params.category_id:
                conditions.append(Job.category_id == params.category_id)
            
            if params.title_search:
                conditions.append(Job.title.ilike(f"%{params.title_search}%"))
            
            if params.tag_search:
                stmt = stmt.join(Job.tags).where(Tag.normalized_name.ilike(f"%{params.tag_search.lower()}%"))
            
            if params.skill_search:
                stmt = stmt.join(Job.skills).where(Skill.normalized_name.ilike(f"%{params.skill_search.lower()}%"))
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            if params.sort_by == 'salary':
                order_col = Job.salary
            elif params.sort_by == 'expires_at':
                order_col = Job.expires_at
            elif params.sort_by == 'title':
                order_col =Job.title
            else:
                order_col = Job.created_at
            
            if params.sort_order == 'asc':
                stmt = stmt.order_by(asc(order_col))
            else:
                stmt = stmt.order_by(desc(order_col))
            
            count_stmt = select(func.count(Job.id)).where(stmt.whereclause)
            total_count = await self.session.scalar(count_stmt)

            offset = (params.page -1) * params.page_size
            stmt = stmt.offset(offset).limit(params.page_size)

            result = await self.session.execute(stmt)
            jobs = result.scalars().all()

            job_responses = [self._convert_to_response(job) for job in jobs]

            return {
                'jobs': job_responses,
                'total': total_count,
                'page': params.page,
                'page_size': params.page_size,
                'total_pages': (total_count + params.page_size - 1) // params.page_size,
                'has_next': params.page * params.page_size < total_count,
                'has_prev': params.page > 1
            }
        except SQLAlchemyError as e:
            logger.error(f'Database error searching job: {str(e)}')
            raise BusinessLogicError('Job search failed')
        
    async def delete_job(self, job_id: int, current_user: UserResponse, hard_delete: bool = False) -> Dict[str, str]:
        logger.info(f'Deletin job {job_id} by user {current_user.id} hard deleted = {hard_delete}')

        try:
            async with self.transaction():
                job = await self._get_job_for_update(job_id, current_user)

                if hard_delete:
                    await self.session.delete(job)
                    message = "Job permanetly deleted"
                else:
                    job.deleted_at = datetime.utcnow()
                    job.deleted_by = current_user.id
                    job.is_active = False

                    message = 'Job deleted successfuly'

                if self.cache:
                    await self._invalidate_job_caches(job)
                
                logger.info(f'Job {job_id} is deleted succesfully')
                return {'message': message}
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting job {job_id}: {str(e)}")
            raise BusinessLogicError("Failed to delete job")
        
    async def _validate_user_company_access(self, user: UserResponse):
        company = await self.session.get(Company, user.company_id)
        if not company:
            raise EntityNotFoundError('Users company not found')
        if not company.is_active:
            raise BusinessLogicError('Cannot create jobs for inactive company')
        
    async def _process_skills(self, skills: List[str]) -> List[Skill]:
        cleaned_skills = clean_and_validate_skills(skills)
        skill_objects = []

        for skill_name in cleaned_skills:
            stmt = select(Skill).where(Skill.normalized_name == skill_name.lower())
            result  = await self.session.execute(stmt)
            skill_obj = result.scalar_one_or_none()

            if not skill_obj:
                skill_obj = Skill(name=skill_name)
                self.session.add(skill_obj)
                await self.session.flush()

                logger.debug(f'Create new skill: {skill_name}')

            skill_objects.append(skill_obj)
        
        return skill_objects

    async def _process_tags(self, tags: List[str]) -> List[Tag]:
        cleaned_tags = clean_and_validate_tags(tags)
        tags_objects = []

        for tag_name in cleaned_tags:
            stmt = select(Tag).where(Tag.normalized_name == tag_name.lower())
            result  = await self.session.execute(stmt)
            tag_obj = result.scalar_one_or_none()

            if not tag_obj:
                tag_obj = Tag(name=tag_name)
                self.session.add(tag_obj)
                await self.session.flush()

                logger.debug(f'Create new tag: {tag_obj}')

            tags_objects.append(tag_obj)
        
        return tags_objects
    
    async def _get_job_for_update(self, job_id: int, user: UserResponse) -> Job:
        stmt = select(Job).where(Job.id == job_id)
        result = await self.session.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise EntityNotFoundError(f"Job with ID {job_id} not found")
        
        if not user.is_admin and job.company != user.company_id:
            raise PermissionDeniedError('You can only update jobs from your company')
        
        if job.deleted_at:
            raise BusinessLogicError('Cannot updated job')
        
        return job
    

    async def _invalidate_job_caches(self, job: Job) -> None:
        if not self.cache:
            return 
        
        cache_keys = [
            f"Job: {job.id}",
            f"company_jobs: {job.company_id}",
            f"category_jos: {job.category_id}",
            "job_search:*"
        ]

        for key in cache_keys:
            await self.cache.delete(key)
    
    def _convert_to_response(self, job: Job) -> JobResponse:
        return JobResponse(
            id=job.id,
            title=job.title,
            description=job.description,
            salary=job.salary,
            location=job.location,
            employment_type=job.employment_type,
            education_level=job.education_level,
            skill_levels=[SkillLevel(level) for level in job.skill_levels],
            skills_required=[skill.name for skill in job.skills],
            tags=[tag.name for tag in job.tags],
            expires_at=job.expires_at,
            company_id=job.company_id,
            category_id=job.category_id,
            is_active=job.is_active,
            created_at=job.created_at,
            updated_at=job.updated_at,
            is_expired=job.is_expired(),
            days_until_expiry=job.days_until_expiry(),
            hours_until_expiry=max(0, int((job.expires_at - datetime.utcnow()).total_seconds() / 3600))

        )