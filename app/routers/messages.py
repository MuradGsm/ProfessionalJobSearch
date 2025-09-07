# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List

# from app.models.messages_model import Message
# from app.schemas.message_schema import MessageCreate, MessageResponse, ChatListResponse
# from app.schemas.user_schema import UserResponse
# from app.db.database import get_session
# from app.auth.deps import get_current_user
# from app.services.messages_service import (
#     get_chat_list_service,
#     get_chat_messages_service,
#     mark_messages_read_service,
#     send_message_service
# )

# router = APIRouter(prefix="/messages", tags=["Chat"])



# @router.get('/{chat_id}', response_model=List[MessageResponse])
# async def get_chat_messages(chat_id: str, session: AsyncSession = Depends(get_session), current_user: UserResponse = Depends(get_current_user)):
#     return await get_chat_messages_service(chat_id, session, current_user)

# @router.get('/chats', response_model=List[ChatListResponse])
# async def get_chat_list(current_user: UserResponse = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
#     return await get_chat_list_service(current_user, session)

# @router.post('/', response_model=MessageResponse)
# async def send_message(message: MessageCreate, current_user: UserResponse  = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
#     return await send_message_service(message, current_user, session)

# @router.put('/{chat_id}')
# async def mark_messages_read(chat_id: str, session: AsyncSession = Depends(get_session), current_user: UserResponse = Depends(get_current_user)):
#     return await mark_messages_read_service(chat_id, session, current_user)