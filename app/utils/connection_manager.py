from fastapi import WebSocket

class ConnectionManager:
    
    def __init__(self):
        self.active_connections: dict[int, WebSocket]= {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()        
        self.active_connections[user_id] = websocket

    
    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
    
    async def send_personal_message(self, message: str, user_id: int):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
        
    

manager = ConnectionManager()