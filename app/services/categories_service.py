from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.jobs_model import Categories, Job
from app.schemas.job_schema import CategoryCreate
from typing import List, Optional

async def get_all_categories_service(
        session: AsyncSession, 
        is_active: Optional[bool] = None,
        parent_id: Optional[int] = None) -> List[Categories]:
    query = select(Categories)

    if is_active is not None:
        query = query.where(Categories.is_active == is_active)
    
    if parent_id is not None:
        query = query.where(Categories.parent_id == parent_id)
    
    results = await session.execute(query)
    categories = results.scalars().all()

    results


async def get_category_service(cat_id: int, session: AsyncSession) -> Categories:
    result = await session.execute(select(Categories).where(Categories.id == cat_id))
    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=' Category is not found')
    
    return category

async def cretae_category_service(cat_data: CategoryCreate, session: AsyncSession) -> Categories:
    category = Categories(**cat_data.dict())

    session.add(category)
    await session.commit()
    await session.refresh(category)

    return category

async def update_category_service(cat_id: int, cat_db: CategoryCreate, session: AsyncSession) -> Categories:
    result = await session.execute(select(Categories).where(Categories.id == cat_id))
    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=' Category is not found')
    
    category.name = cat_db.name
    category.description = cat_db.description
    category.is_active = cat_db.is_active
    category.parent_id = cat_db.parent_id

    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

async def delete_category_service(cat_id: int, session: AsyncSession) -> dict:
    result = await session.execute(select(Categories).where(Categories.id == cat_id))
    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=' Category is not found')
    
    session.delete(category)
    await session.commit()
    return {'message': 'Category successfuly deleted!'}


async def active_jobs_count(cat_id: int, session: AsyncSession) -> int:
        """Count of active jobs in this category using SQL aggregation"""

        result = session.execute(
            select(func.count(Job.id))
            .where(and_(
                Job.category_id == cat_id,
                Job.is_active ==True,
                Job.expires_at > func.now()
            ))
        ).scalar()
        return result or 0