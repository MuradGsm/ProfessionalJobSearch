from typing import List, Dict, Set
from fastapi import WebSocket
from app.schemas.notification_schema import NotificationSchema
from app.models.messages_model import Message

users_db = []
jobs_db = []
resumes_db = []
aplications_db = []
notification_db: List[NotificationSchema] = []

connections: Dict[str, List[WebSocket]] = {}

messages_db: Dict[str, List[Message]] = {} 

socket_rooms: Dict[WebSocket, str] = {}

active_users: Dict[int, WebSocket] = {}

def create_chat_id(user1_id: int, user2_id: int) -> str:
    """Create consistent chat_id from two user IDs"""
    return f"{min(user1_id, user2_id)}-{max(user1_id, user2_id)}"

def get_other_user_id(chat_id: str, current_user_id: int) -> int:
    """Get the other user's ID from chat_id"""
    user_ids = chat_id.split('-')
    user1_id, user2_id = int(user_ids[0]), int(user_ids[1])
    return user2_id if current_user_id == user1_id else user1_id


