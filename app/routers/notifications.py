from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.notification_schema import NotificationCreate, NotificationSchema
from app.schemas.user_schema import UserResponse
from app.db.database import get_session
from app.auth.deps import get_current_user
from app.services.notifications_service import (
    get_notifications_by_user_service,
    create_notification_service,
    mark_notification_read_service,
    delete_notification_service
)

router = APIRouter(prefix='/notification', tags=['notifications'])


@router.get('/', response_model=List[NotificationSchema])
async def get_notifications_by_user(session:AsyncSession = Depends(get_session), current_user: UserResponse = Depends(get_current_user)):
    return await get_notifications_by_user_service(session, current_user)

@router.post('/', response_model=NotificationSchema)
async def create_notification(
    notif: NotificationCreate, 
    session:AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)):
    return await create_notification_service(notif, session)

@router.put('/{notf_id}', response_model=NotificationSchema)
async def mark_notification_read(
    notf_id: int,
    session:AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    return await mark_notification_read_service(session, notf_id, current_user)

@router.delete('/{notf_id}')
async def delete_notification(
    notf_id: int,
    session:AsyncSession = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    return await delete_notification_service(session, notf_id, current_user)