from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.utils.enums import UserRole
from app.models.users_model import User
from app.models.resumes_model import Resume
from app.schemas.resume_schema import ResumeCreate

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


resume_service = ResumeService()
