from fastapi import HTTPException, status
from app.db.fake_db import aplications_db, jobs_db, notification_db
from app.schemas.aplication_schema import ApplicationResponse, ApplicationWithNotificationResponse
from app.schemas.user_schema import UserResponse
from app.schemas.notification_schema import NotificationSchema
from typing import List
from datetime import datetime


async def get_all_aplications_service(current_user: UserResponse) -> List[ApplicationResponse]:
    return [app for app in aplications_db if app.user_id == current_user.id]


async def add_aplication_service(
    job_id: int, 
    current_user: UserResponse, 
    status: str = 'sent'
) -> ApplicationWithNotificationResponse:
    job = next((j for j in jobs_db if j.id == job_id), None)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found')

    new_id = len(aplications_db) + 1
    application = ApplicationResponse(
        id=new_id,
        user_id=current_user.id,
        job_id=job.id,
        status=status
    )
    aplications_db.append(application)

    notification_id = len(notification_db) + 1 if notification_db else 1
    notification = NotificationSchema(
        id=notification_id,
        user_id=current_user.id,
        type="application",
        content=f"Вы откликнулись на вакансию: {job.title}",
        is_read=False,
        created_at=datetime.utcnow().isoformat()
    )
    notification_db.append(notification)

    return ApplicationWithNotificationResponse(
        application=application,
        notification=notification
    )


async def update_aplication_service(application_id: int, status: str, current_user: UserResponse) -> ApplicationResponse:
    index = next((i for i, a in enumerate(aplications_db) if a.id == application_id), None)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Application not found')

    if aplications_db[index].user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to update this application')

    old_app = aplications_db[index]
    updated_app = ApplicationResponse(
        id=old_app.id,
        job_id=old_app.job_id,
        user_id=old_app.user_id,
        status=status
    )
    aplications_db[index] = updated_app
    return updated_app



