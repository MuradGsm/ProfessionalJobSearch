from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List

from app.models.aplications_model import Application, ApplicationStatus
from app.models.jobs_model import Job
from app.models.notifications_model import Notification
from app.schemas.application_schema import ApplicationResponse, ApplicationWithNotificationResponse
from app.schemas.user_schema import UserResponse


async def get_all_applications_service(current_user: UserResponse, session: AsyncSession) -> List[Application]:
    query = select(Application).where(Application.user_id == current_user.id)
    result = await session.execute(query)
    applications = result.scalars().all()
    return applications


async def add_application_service(
    session: AsyncSession,
    job_id: int,
    current_user: UserResponse,
    status: str = "sent"
) -> ApplicationWithNotificationResponse:

    existing_query = select(Application).where(
        Application.user_id == current_user.id,
        Application.job_id == job_id
    )
    existing_result = await session.execute(existing_query)
    existing_application = existing_result.scalar_one_or_none()
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job"
        )

    job_query = select(Job).where(Job.id == job_id)
    job_result = await session.execute(job_query)
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    status_enum = ApplicationStatus(status)
    new_application = Application(
        user_id=current_user.id,
        job_id=job.id,
        status=status_enum
    )
    session.add(new_application)
    await session.commit()
    await session.refresh(new_application)

    new_notification = Notification(
        user_id=current_user.id,
        type="application",
        content=f"You applied for the job: {job.title}",
        is_read=False,
        created_at=datetime.utcnow()
    )
    session.add(new_notification)
    await session.commit()
    await session.refresh(new_notification)

    return ApplicationWithNotificationResponse(
        application=new_application,
        notification=new_notification
    )

async def update_application_service(
    application_id: int,
    status: str,
    current_user: UserResponse,
    session: AsyncSession
) -> ApplicationResponse:

    query = select(Application).where(Application.id == application_id)
    result = await session.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this application"
        )

    application.status = ApplicationStatus(status)
    session.add(application)
    await session.commit()
    await session.refresh(application)

    return ApplicationResponse(
        id=application.id,
        job_id=application.job_id,
        user_id=application.user_id,
        status=application.status.value
    )


async def delete_application_service(
    application_id: int,
    current_user: UserResponse,
    session: AsyncSession
) -> dict:

    query = select(Application).where(Application.id == application_id)
    result = await session.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this application"
        )

    await session.delete(application)
    await session.commit()

    return {"message": "Application deleted successfully"}
