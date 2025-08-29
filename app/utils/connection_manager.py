from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
import json
from app.db.fake_db import connections, socket_rooms, active_users, create_chat_id
from app.services.messages_service import MessageService

class ConnectionManager:
    
    def __init__(self):
        self.connections = connections
        self.socket_rooms = socket_rooms
        self.active_users = active_users
    
    async def connect(self, websocket: WebSocket, user_id: int, other_user_id: int):
        await websocket.accept()
        
        chat_id = create_chat_id(user_id, other_user_id)

        if chat_id not in self.connections:
            self.connections[chat_id] = []
        self.connections[chat_id].append(websocket)

        self.socket_rooms[websocket] = chat_id

        self.active_users[user_id] = websocket

        await self.send_chat_history(websocket, chat_id)
        
        return chat_id
    
    def disconnect(self, websocket: WebSocket):
        """Отключить пользователя"""

        if websocket in self.socket_rooms:
            chat_id = self.socket_rooms[websocket]
            if chat_id in self.connections:
                self.connections[chat_id].remove(websocket)
                if not self.connections[chat_id]:  
                    del self.connections[chat_id]
            del self.socket_rooms[websocket]
        
        user_to_remove = None
        for user_id, ws in self.active_users.items():
            if ws == websocket:
                user_to_remove = user_id
                break
        if user_to_remove:
            del self.active_users[user_to_remove]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Отправить сообщение конкретному соединению"""
        await websocket.send_text(message)
    
    async def broadcast_to_chat(self, message: str, chat_id: str):
        """Отправить сообщение всем участникам чата"""
        if chat_id in self.connections:
            for websocket in self.connections[chat_id]:
                try:
                    await websocket.send_text(message)
                except:
                    self.connections[chat_id].remove(websocket)
    
    async def send_chat_history(self, websocket: WebSocket, chat_id: str):
        """Отправить историю сообщений при подключении"""
        messages = MessageService.get_chat_messages(chat_id)
        
        history_data = {
            "type": "chat_history",
            "messages": [
                {
                    "user_id": msg.user_id,
                    "sender_role": msg.sender_role,
                    "text": msg.text,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        
        await self.send_personal_message(json.dumps(history_data), websocket)
    
    async def handle_message(
        self, 
        websocket: WebSocket, 
        data: dict, 
        current_user_id: int, 
        current_user_role: str
    ):
        """Обработать входящее сообщение"""
        message_type = data.get("type")
        
        if message_type == "send_message":
            text = data.get("text", "").strip()
            if not text:
                await self.send_error(websocket, "Сообщение не может быть пустым")
                return
            
            chat_id = self.socket_rooms.get(websocket)
            if not chat_id:
                await self.send_error(websocket, "Не удалось определить чат")
                return

            other_user_id = None
            user_ids = chat_id.split('-')
            for uid in user_ids:
                if int(uid) != current_user_id:
                    other_user_id = int(uid)
                    break
            
            if not other_user_id:
                await self.send_error(websocket, "Не удалось определить получателя")
                return

            message = MessageService.create_message(
                sender_id=current_user_id,
                recipient_id=other_user_id,
                text=text,
                sender_role=current_user_role
            )

            message_data = {
                "type": "new_message",
                "user_id": message.user_id,
                "sender_role": message.sender_role,
                "text": message.text,
                "created_at": message.created_at.isoformat()
            }
            
            await self.broadcast_to_chat(json.dumps(message_data), chat_id)
    
    async def send_error(self, websocket: WebSocket, error_message: str):
        """Отправить сообщение об ошибке"""
        error_data = {
            "type": "error",
            "message": error_message
        }
        await self.send_personal_message(json.dumps(error_data), websocket)

manager = ConnectionManager()