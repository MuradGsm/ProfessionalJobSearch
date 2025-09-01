from fastapi import HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, case, and_, update
from datetime import datetime
from app.schemas.message_schema import MessageResponse, ChatListResponse, MessageCreate
from app.schemas.user_schema import UserResponse
from app.models.messages_model import Message
from app.models.users_model import User


async def send_message_service(message: MessageCreate, current_user: UserResponse, session: AsyncSession) -> Message:
    recipient = await session.get(User, message.recipient_id)
    
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Recipient not found')
    
    if current_user.id == message.recipient_id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    chat_id = Message.generate_chat_id(current_user.id, message.recipient_id)
    new_message = Message(
        chat_id=chat_id,
        sender_id=current_user.id,
        recipient_id=message.recipient_id,
        text=message.text.strip()
    )

    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)
    return new_message


async def get_chat_messages_service(chat_id: str, session: AsyncSession, current_user: UserResponse) -> List[Message]:
    user_ids = chat_id.replace('chat_', '').split('_')
    if str(current_user.id) not in user_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    results = await session.execute(
        select(Message).where(
            and_(
                Message.chat_id == chat_id,
                or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id)
            )
        ).order_by(Message.created_at.asc())
    )
    messages = results.scalars().all()
    return messages


async def get_chat_list_service(current_user: UserResponse, session: AsyncSession) -> List[ChatListResponse]:
    subq = (
        select(
            Message.chat_id, 
            func.max(Message.created_at).label("last_time")
        ).where(
            and_(
                or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id),
            )
        ).group_by(Message.chat_id).subquery()
    )

    companion_id = case(
        (Message.sender_id == current_user.id, Message.recipient_id),
        else_=Message.sender_id
    ).label('companion_id')

    unread_subq = (
        select(
            Message.chat_id,
            func.count(Message.id).label("unread_count")
        ).where(
            and_(
                Message.recipient_id == current_user.id,
                Message.is_read == False,
            )
        ).group_by(Message.chat_id).subquery()
    )

    query = (
        select(
            Message.chat_id,
            Message.text.label("last_message"),
            Message.created_at.label("last_message_time"),
            User.id.label("other_user_id"),
            User.name.label("other_user_name"),
            User.role.label("other_user_role"),
            func.coalesce(unread_subq.c.unread_count, 0).label("unread_count")
        )
        .join(subq, and_(
            subq.c.chat_id == Message.chat_id,
            subq.c.last_time == Message.created_at
        ))
        .join(User, User.id == companion_id)
        .outerjoin(unread_subq, unread_subq.c.chat_id == Message.chat_id)
        .order_by(Message.created_at.desc())
    )

    results = await session.execute(query)
    rows = results.all()

    chat_list: List[ChatListResponse] = [
        ChatListResponse(
            chat_id=row.chat_id,
            last_message=row.last_message,
            last_message_time=row.last_message_time,
            other_user_id=row.other_user_id,
            other_user_name=row.other_user_name,
            other_user_role=row.other_user_role,
            unread_count=row.unread_count or 0
        )
        for row in rows
    ]

    return chat_list


async def mark_messages_read_service(chat_id: str, session: AsyncSession, current_user: UserResponse) -> dict:
    user_ids = chat_id.replace('chat_', '').split('_')
    if str(current_user.id) not in user_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    result = await session.execute(
        update(Message).where(
            and_(
                Message.chat_id == chat_id,
                Message.recipient_id == current_user.id,
                Message.is_read == False
            )
        ).values(is_read=True)
    )
    
    await session.commit()
    return {"marked_count": result.rowcount}