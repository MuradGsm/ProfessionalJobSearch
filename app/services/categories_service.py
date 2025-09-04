from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.jobs_model import Categories
from app.schemas.job_schema import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_category(self, data: CategoryCreate) -> Categories:
        exists = await self.session.scalar(select(Categories).where(Categories.name == data.name))

        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category name exists')
        
        parent = None
        if data.parent_id:
            parent = await self.session.get(Categories, data.parent_id) 
            if not parent:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent category not found')
            
        category = Categories(
            name=data.name,
            description=data.description,
            is_active=data.is_active,
            parent_id=data.parent_id
        )
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def get_category(self, cat_id: int) -> Categories:
        category = await self.session.get(Categories, cat_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
        return category  # ИСПРАВЛЕНО: добавлен return
        
    async def list_categories(self, active_only: bool = True) -> List[Categories]:
        query = select(Categories)
        if active_only:
            query = query.where(Categories.is_active == True)
        
        result = await self.session.scalars(query)
        return result.all()

    async def update_category(self, cat_id: int, cat_data: CategoryUpdate) -> Categories:
        category = await self.get_category(cat_id)  
        
        if cat_data.name and cat_data.name != category.name:
            exists = await self.session.scalar(
                select(Categories).where(Categories.name == cat_data.name)
            )
            if exists:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category name exists')
            category.name = cat_data.name 
            
        if cat_data.description:
            category.description = cat_data.description
        
        if cat_data.is_active is not None:
            category.is_active = cat_data.is_active

        if cat_data.parent_id is not None:
            if cat_data.parent_id != category.parent_id:
                parent = await self.session.get(Categories, cat_data.parent_id)
                if not parent:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent category not found')

                category.parent_id = cat_data.parent_id
                if category.has_cycle():
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cyclic category hierarchy is not allowed')
        
        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def delete_category(self, cat_id: int, soft: bool = True) -> dict:
        category = await self.get_category(cat_id)

        if soft:
            category.is_active = False
            await self.session.commit()
        else:
            if category.jobs or category.children:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete category with subcategories or active jobs')
            
            await self.session.delete(category)
            await self.session.commit()
        
        return {'message': 'Category deleted'} 