from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.utils.enums import UserRole
from app.models.users_model import User
from app.models.resumes_model import Resume
from app.schemas.resume_schema import ResumeCreate, ResumeUpdate

import logging

logger = logging.getLogger(__name__)

class ResumeService:
    def __init__(self):
        pass

    async def create_resume_service(self, db: AsyncSession, current_user: User, data: ResumeCreate):
        if current_user.role != 'candidate':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This method not allowed')

        query = select(Resume).where(Resume.user_id == current_user.id)
        resumes = (await db.execute(query)).scalars().all()

        slug = f"{data.title.lower().replace(' ', '-')}-{current_user.id}"

        new_resume = Resume(
            **data.dict(),
            slug=slug,
            user_id=current_user.id
        )

        db.add(new_resume)
        await db.commit()
        await db.refresh(new_resume)
        return new_resume

    async def update_resume_service(self, resume_id: int, data: ResumeUpdate, db: AsyncSession, current_user: User):
        stmt = await db.execute(select(Resume).where(Resume.id == resume_id))
        resume = stmt.scalar_one_or_none()

        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
        
        if resume.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Method not allowed')
        
        for field, value in data.dict(exclude_unset=True).items():
            setattr(resume, field, value)
        
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        return resume 
        




resume_service = ResumeService()
