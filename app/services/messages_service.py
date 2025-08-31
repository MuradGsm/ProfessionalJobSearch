from typing import List, Optional
from datetime import datetime
from app.db.fake_db import (
    messages_db, users_db, create_chat_id, get_other_user_id
)
from app.schemas.message_schema import  MessageResponse, ChatListResponse
from app.schemas.user_schema import UserResponse
from app.models.messages_model import Message

class MessageService:
    
    @staticmethod
    def create_message(
        sender_id: int, 
        recipient_id: int, 
        text: str, 
        sender_role: str
    ) -> Message:
        """Создать новое сообщение"""
        chat_id = create_chat_id(sender_id, recipient_id)
        
        message = Message(
            chat_id=chat_id,
            user_id=sender_id,
            sender_role=sender_role,
            text=text,
            created_at=datetime.utcnow()
        )
        
        if chat_id not in messages_db:
            messages_db[chat_id] = []
        messages_db[chat_id].append(message)
        
        return message
    
    @staticmethod
    def get_chat_messages(chat_id: str) -> List[MessageResponse]:
        """Получить все сообщения чата"""
        messages = messages_db.get(chat_id, [])
        return [
            MessageResponse(
                chat_id=msg.chat_id,
                user_id=msg.user_id,
                sender_role=msg.sender_role,
                text=msg.text,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    
    @staticmethod
    def get_user_chats(user_id: int) -> List[ChatListResponse]:
        """Получить список всех чатов пользователя"""
        user_chats = []
        
        for chat_id, messages in messages_db.items():
            if messages:  
                user_ids = chat_id.split('-')
                if str(user_id) in user_ids:
                    other_user_id = get_other_user_id(chat_id, user_id)

                    other_user = MessageService._get_user_by_id(other_user_id)
                    if other_user:
                        last_message = messages[-1] if messages else None
                        
                        user_chats.append(ChatListResponse(
                            chat_id=chat_id,
                            other_user_id=other_user_id,
                            other_user_name=other_user.name,
                            other_user_role=other_user.role,
                            last_message=last_message.text if last_message else None,
                            last_message_time=last_message.created_at if last_message else None
                        ))
        
        user_chats.sort(
            key=lambda x: x.last_message_time or datetime.min, 
            reverse=True
        )
        
        return user_chats
    
    @staticmethod
    def _get_user_by_id(user_id: int) -> Optional[UserResponse]:
        """Найти пользователя по ID"""
        for user in users_db:
            if user.id == user_id:
                return user
        return None
    
    @staticmethod
    def validate_chat_participants(user1_id: int, user2_id: int) -> bool:
        """Проверить, существуют ли оба пользователя"""
        user1 = MessageService._get_user_by_id(user1_id)
        user2 = MessageService._get_user_by_id(user2_id)
        return user1 is not None and user2 is not None