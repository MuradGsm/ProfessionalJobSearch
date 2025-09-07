import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.job_schema import CategoryCreate, CategoryResponse, CategoryStats, CategoryUpdate
from app.models.jobs_model import Categories, Job
from app.config.cache import CacheManager
from app.config.exceptions import BusinessLogicError, EntityNotFoundError, ValidationError


logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, session: AsyncSession, cache_manager: Optional[CacheManager] = None):
        self.cache = cache_manager
        self.session = session
        self.cache_ttl = 3600

    @asynccontextmanager
    async def transaction(self):
        try:
            yield
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f'Transation rolled back: {str(e)}')
            raise

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        logger.info(f"Creating ctaegory: {data.name}")

        try:
            async with self.transaction():

                exists_stmt = select(Categories).where(Categories.name.ilike(data.name.strip()))
                existing = await self.session.scalar(exists_stmt)

                if existing:
                    raise ValidationError(f'Category with name "{data.name}" already exists')
                
                if data.parent_id:
                    parent = await self.session.get(Categories, data.parent_id) 
                    if not parent:
                        raise EntityNotFoundError('Parent category not found')
                    if not parent.is_active:
                        raise ValidationError('Cannot create subcategory under inactive parent')
                    

                category = Categories(
                    name=data.name.strip(),
                    description=data.description.strip(),
                    is_active=data.is_active,
                    parent_id=data.parent_id
                )

                self.session.add(category)
                await self.session.flush()

                if category.has_cycle():
                    raise ValidationError('Cycle category hierarch is not allowed')
                
                await self.session.refresh(category, ['children'])

                if self.cache:
                    await self._invalidate_category_caches()
                

                logger.info(f"Category created successfully: ID {category.id}, Name: '{category.name}'")
                return self._convert_to_response(category)
        except IntegrityError as e:
            logger.error(f'Database integrity error creating category: {str(e)}')
            raise ValidationError('Category creation failed due to data constraint violation')
        except SQLAlchemyError as e:
            logger.error(f'Database error creating: {str(e)}')
            raise BusinessLogicError('Category creation failed due to database error')
        except Exception as e:
            logger.error(f"Unexpected error creating category: {str(e)}")
    
    async def get_category(self, cat_id: int, use_cache: bool = True) -> CategoryResponse:

        cache_key = f"category:{cat_id}"
        if self.cache and use_cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"Category {cat_id} returned from cache")
                return CategoryResponse.model_validate(cached)
        
        try:
            stmt = select(Categories).options(selectinload(Categories.children)).where(Categories.id == cat_id)   
            result = await self.session.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                raise EntityNotFoundError('Category not found')
            category_response =self._convert_to_response(category)

            if self.cache and use_cache:
                await self.cache.set(cache_key, category_response.model_dump(), expire=self.cache_ttl)

            return category_response 
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching category {cat_id}: {str(e)}")
            raise BusinessLogicError('Failed to fetch category')
        
    async def list_categories(self, 
                              active_only: bool = True, 
                              include_job_count: bool = False, 
                              use_cache: bool = True, 
                              parent_id: Optional[int] = None) -> List[CategoryResponse]:
        
        cache_key = f"categories:active_{active_only}:jobs_{include_job_count}"

        if self.cache and use_cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug("Categories returned from cache")
                return [CategoryResponse.model_validate(cat) for cat in cached]
        
        try:
            if include_job_count:
                stmt = stmt = select(
                    Categories,
                    func.count(Job.id).label('job_count')
                ).outerjoin(
                    Job, and_(
                        Job.category_id == Categories.id,
                        Job.is_active == True,
                        Job.deleted_at.is_(None)
                    )
                ).options(selectinload(Categories.children)).group_by(Categories.id)
            else:
                stmt = select(Categories).options(selectinload(Categories.children))

            conditions = []

            if active_only:
                conditions.append(Categories.is_active == True)
            
            if parent_id is not None:
                conditions.append(Categories.parent_id == parent_id)

            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(Categories.name)

            result = await self.session.execute(stmt)

            if include_job_count:
                categories_with_count = result.all()
                categories = []
                for category, job_count in categories_with_count:
                    cat_response = self._convert_to_response(category)
                    cat_response.active_jobs_count = job_count or 0
                    categories.append(cat_response)
            else:
                categories = [
                    self._convert_to_response(cat) for cat in result.scalars().all()
                ]
            
            if self.cache and use_cache:
                cache_data = [cat.model_dump() for cat in categories]
                await self.cache.set(cache_key, cache_data, expire=self.cache_ttl)

            logger.debug(f"Retrieved {len(categories)} categories")
            return categories 
        except SQLAlchemyError as e:
            logger.error(f"Database error listing categories: {str(e)}")
            raise BusinessLogicError('Failed to list categories') 
            
    async def update_category(self, cat_id: int, cat_data: CategoryUpdate) -> CategoryResponse:
        logger.info(f"Updating category {cat_id}")
        
        try:
            async with self.transaction():
                category = await self._get_category_for_update(cat_id)
                
                update_data = cat_data.model_dump(exclude_unset=True)
                
                if 'name' in update_data and update_data['name'] != category.name:
                    exists_stmt = select(Categories).where(
                        and_(
                            Categories.name.ilike(update_data['name'].strip()),
                            Categories.id != cat_id
                        )
                    )
                    if await self.session.scalar(exists_stmt):
                        raise ValidationError('Category name already exists')
                    category.name = update_data['name'].strip()
                
                for field, value in update_data.items():
                    if field == 'name':
                        continue  # Already handled above
                    elif field == 'description' and value:
                        category.description = value.strip()
                    elif field == 'parent_id':
                        await self._update_parent_category(category, value)
                    elif hasattr(category, field) and value is not None:
                        setattr(category, field, value)
                
                await self.session.flush()
                
                if category.has_cycle():
                    raise ValidationError('Update would create cyclic category hierarchy')
                
                await self.session.refresh(category, ['children'])
                
                if self.cache:
                    await self._invalidate_category_caches()
                
                logger.info(f"Category {cat_id} updated successfully")
                return self._convert_to_response(category)
                
        except SQLAlchemyError as e:
            logger.error(f"Database error updating category {cat_id}: {str(e)}")
            raise BusinessLogicError('Failed to update category')

    async def delete_category(self, cat_id: int, soft_delete: bool = True) -> Dict[str, str]:
        logger.info(f"Deleting category {cat_id}, soft_delete={soft_delete}")
        
        try:
            async with self.transaction():
                category = await self._get_category_for_update(cat_id)
                
                job_count = await self.session.scalar(
                    select(func.count(Job.id)).where(
                        and_(
                            Job.category_id == cat_id,
                            Job.is_active == True,
                            Job.deleted_at.is_(None)
                        )
                    )
                )
                
                child_count = await self.session.scalar(
                    select(func.count(Categories.id)).where(
                        and_(
                            Categories.parent_id == cat_id,
                            Categories.is_active == True
                        )
                    )
                )
                
                if soft_delete:
                    if job_count > 0:
                        raise ValidationError(f'Cannot delete category with {job_count} active jobs')
                    if child_count > 0:
                        raise ValidationError(f'Cannot delete category with {child_count} active subcategories')
                    
                    category.is_active = False
                    message = "Category deactivated successfully"
                else:
                    if job_count > 0 or child_count > 0:
                        raise ValidationError('Cannot permanently delete category with jobs or subcategories')
                    
                    await self.session.delete(category)
                    message = "Category permanently deleted"
                
                if self.cache:
                    await self._invalidate_category_caches()
                
                logger.info(f"Category {cat_id} deleted successfully")
                return {'message': message}
                
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting category {cat_id}: {str(e)}")
            raise BusinessLogicError('Failed to delete category')

    async def get_category_tree(self, use_cache: bool = True) -> List[CategoryResponse]:
        cache_key = "category_tree"
        
        if self.cache and use_cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug("Category tree returned from cache")
                return [CategoryResponse.model_validate(cat) for cat in cached]
        
        try:
            root_categories = await self.list_categories(
                active_only=True, 
                include_job_count=True,
                parent_id=None,
                use_cache=False
            )
            
            for category in root_categories:
                await self._build_category_tree(category)
            
            if self.cache and use_cache:
                cache_data = [cat.model_dump() for cat in root_categories]
                await self.cache.set(cache_key, cache_data, expire=self.cache_ttl)
            
            return root_categories
            
        except Exception as e:
            logger.error(f"Error building category tree: {str(e)}")
            raise BusinessLogicError('Failed to build category tree')

    async def get_category_stats(self) -> CategoryStats:
        try:
            total_categories = await self.session.scalar(
                select(func.count(Categories.id))
            )
            
            active_categories = await self.session.scalar(
                select(func.count(Categories.id)).where(Categories.is_active == True)
            )
            
            categories_with_jobs = await self.session.scalar(
                select(func.count(func.distinct(Job.category_id))).where(
                    and_(Job.is_active == True, Job.deleted_at.is_(None))
                )
            )
            
            avg_jobs_per_category = await self.session.scalar(
                select(func.avg(func.count(Job.id))).select_from(
                    select(Job.category_id, func.count(Job.id)).where(
                        and_(Job.is_active == True, Job.deleted_at.is_(None))
                    ).group_by(Job.category_id).subquery()
                )
            ) or 0.0
            
            return CategoryStats(
                total_categories=total_categories or 0,
                active_categories=active_categories or 0,
                categories_with_jobs=categories_with_jobs or 0,
                avg_jobs_per_category=round(avg_jobs_per_category, 2)
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting category stats: {str(e)}")
            raise BusinessLogicError('Failed to get category statistics')

    # Private helper methods
    async def _get_category_for_update(self, cat_id: int) -> Categories:
        stmt = select(Categories).where(Categories.id == cat_id)
        result = await self.session.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            raise EntityNotFoundError(f'Category with ID {cat_id} not found')
        
        return category

    async def _update_parent_category(self, category: Categories, new_parent_id: Optional[int]):
        if new_parent_id == category.parent_id:
            return
        
        if new_parent_id is not None:
            parent = await self.session.get(Categories, new_parent_id)
            if not parent:
                raise EntityNotFoundError('Parent category not found')
            if not parent.is_active:
                raise ValidationError('Cannot set inactive category as parent')
        
        category.parent_id = new_parent_id

    async def _build_category_tree(self, category: CategoryResponse):
        if category.children:
            for child in category.children:
                await self._build_category_tree(child)

    async def _invalidate_category_caches(self):
        if not self.cache:
            return
        
        cache_patterns = [
            "category:*",
            "categories:*", 
            "category_tree",
            "job_search:*"  
        ]
        
        for pattern in cache_patterns:
            await self.cache.delete(pattern)

    def _convert_to_response(self, category: Categories) -> CategoryResponse:
        return CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            parent_id=category.parent_id,
            children=[self._convert_to_response(child) for child in (category.children or [])],
            active_jobs_count=getattr(category, 'active_jobs_count', 0),
            created_at=category.created_at,
            updated_at=category.updated_at
        )