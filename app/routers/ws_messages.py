from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.auth.deps import get_current_user
from app.schemas.user_schema import UserResponse
from app.schemas.message_schema import MessageCreate
from app.utils.connection_manager import manager
from app.db.database import get_session
from app.services.messages_service import send_message_service

router = APIRouter(prefix="/ws/messages", tags=["WebSocket Chat"])


@router.websocket('/')
async def websocket_endpoint(websocket: WebSocket, token: str,  session = Depends(get_session)):
    current_user: UserResponse = await get_current_user(token)
    await manager.connect(current_user.id, websocket)

    try:
        data = await websocket.receive_text()
        recipient_id = data['recipient_id']
        text = data['text']

        message = await send_message_service(
            MessageCreate(recipient_id, text), current_user, text
        )

        await manager.send_personal_message(message.text, recipient_id)

    except WebSocketDisconnect:
        manager.disconnect(current_user.id)