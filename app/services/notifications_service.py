from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notifications_model import Notification
from app.schemas.notification_schema import NotificationSchema, NotificationCreate
from app.schemas.user_schema import UserResponse

async def create_notification_service(
        notif: NotificationCreate, 
        session: AsyncSession 
        ) -> NotificationSchema:
    notification = Notification(
        type= notif.type,
        content = notif.content,
        user_id = notif.user_id
    )

    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification

async def get_notifications_by_user_service(session: AsyncSession, current_user: UserResponse) -> Notification:
    results = await session.execute(select(Notification).where(Notification.user_id == current_user.id))
    notification = results.scalars().all()
    return notification

async def mark_notification_read_service(session: AsyncSession, not_id: int, current_user: UserResponse) -> Notification:
    results  = await session.execute(select(Notification).where(  Notification.id == not_id,
    Notification.user_id == current_user.id))
    notification = results.scalar_one_or_none()

    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Notification not found')
    
    notification.is_read = True

    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


async def delete_notification_service(session: AsyncSession, not_id: int, current_user: UserResponse) -> dict:
    results  = await session.execute(select(Notification).where(Notification.id == not_id,
    Notification.user_id == current_user.id))
    notification = results.scalar_one_or_none()

    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Notification not found')
    
    session.delete(notification)
    await session.commit()
    return {'message': 'Notifications successfully deleted'}