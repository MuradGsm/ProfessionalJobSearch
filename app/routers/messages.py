from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from typing import List
import json
from app.schemas.message_schema import ChatListResponse
from app.services.messages_service import MessageService
from app.utils.connection_manager import manager
from app.auth.jwt import decode_access_token
from app.auth.deps import get_current_user
from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.websocket("/ws/{other_user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    other_user_id: int,
    token: str = Query(...)
):
    """WebSocket соединение для чата между двумя пользователями"""
    try:
        current_user_id = decode_access_token(token)
        
        current_user = None
        from app.db.fake_db import users_db
        for user in users_db:
            if user.id == current_user_id:
                current_user = user
                break
        
        if not current_user:
            await websocket.close(code=4001, reason="User not found")
            return

        if not MessageService.validate_chat_participants(current_user_id, other_user_id):
            await websocket.close(code=4002, reason="Invalid chat participants")
            return

        chat_id = await manager.connect(websocket, current_user_id, other_user_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                
                try:
                    message_data = json.loads(data)
                    await manager.handle_message(
                        websocket=websocket,
                        data=message_data,
                        current_user_id=current_user_id,
                        current_user_role=current_user.role
                    )
                except json.JSONDecodeError:
                    await manager.send_error(websocket, "Неверный формат JSON")
                except Exception as e:
                    await manager.send_error(websocket, f"Ошибка обработки сообщения: {str(e)}")
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            
    except Exception as e:
        await websocket.close(code=4000, reason=f"Authentication failed: {str(e)}")

@router.get("/chats", response_model=List[ChatListResponse])
async def get_user_chats(current_user: UserResponse = Depends(get_current_user)):
    """Получить список всех чатов текущего пользователя"""
    return MessageService.get_user_chats(current_user.id)

@router.get("/chats/{other_user_id}/messages")
async def get_chat_messages(
    other_user_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """Получить историю сообщений конкретного чата"""

    if not MessageService.validate_chat_participants(current_user.id, other_user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    from app.db.fake_db import create_chat_id
    chat_id = create_chat_id(current_user.id, other_user_id)
    messages = MessageService.get_chat_messages(chat_id)
    
    return {
        "chat_id": chat_id,
        "messages": messages
    }

@router.get("/active-users")
async def get_active_users(current_user: UserResponse = Depends(get_current_user)):
    """Получить список активных пользователей"""
    from app.db.fake_db import active_users, users_db
    
    active_user_list = []
    for user_id in active_users.keys():
        for user in users_db:
            if user.id == user_id and user.id != current_user.id:
                active_user_list.append({
                    "id": user.id,
                    "name": user.name,
                    "role": user.role,
                    "is_active": True
                })
                break
    
    return active_user_list