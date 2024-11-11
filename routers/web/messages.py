
from dataclasses import dataclass
from datetime import datetime
import json
import uuid
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from common.template_config import CustomJinja2Templates
from services import messages_services
import common.auth



router = APIRouter(prefix='/messages', tags=['Messages'])
templates = CustomJinja2Templates(directory="templates")


@dataclass
class ConnectionManager:
  def __init__(self) -> None:
    self.active_connections: dict = {}

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    id = str(uuid.uuid4())
    self.active_connections[id] = websocket

    await self.send_message(websocket, json.dumps({"isMe": True, "data": "Have joined!!", "username": "You", "time": datetime.now().strftime('%H:%M:%S')}))

  async def send_message(self, ws: WebSocket, message: str):
    await ws.send_text(message)

  def find_connection_id(self, websocket: WebSocket):
    websocket_list = list(self.active_connections.values())
    id_list = list(self.active_connections.keys())

    pos = websocket_list.index(websocket)
    return id_list[pos]

  async def broadcast(self, webSocket: WebSocket, data: str):
    decoded_data = json.loads(data)
    timestamp = datetime.now().strftime('%H:%M:%S') 

    username = decoded_data.get('username')
    message = decoded_data.get('message')

    if not message or not username:
        print("Invalid message data, skipping broadcast:", decoded_data)
        return

    for connection in self.active_connections.values():
        is_me = (connection == webSocket)
        
        await connection.send_text(json.dumps({
            "isMe": is_me,
            "data": message,
            "username": username,
            "time": timestamp
        }))

  def disconnect(self, websocket: WebSocket):
    id = self.find_connection_id(websocket)
    del self.active_connections[id]

    return id


manager = ConnectionManager()


@router.get("/", response_class=HTMLResponse)
def get_room(request: Request):

  current_user = common.auth.get_current_user(request.cookies.get('token'))

  if not current_user:
    return templates.TemplateResponse("users.html", {"error": "You need to login first", "request": request})

  return templates.TemplateResponse("message.html", {"request": request})

@router.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
  # Accept the connection from the client.
  await manager.connect(websocket)

  try:
    while True:
      # Recieves message from the client
      data = await websocket.receive_text()
      message_data = json.loads(data)
      if "sender_id" not in message_data or "receiver_id" not in message_data:
            await websocket.send_text(json.dumps({"error": "sender_id and receiver_id are required"}))
            continue
      
      messages_services.create_message(message_data['message'], message_data['sender_id'], message_data['receiver_id'])
      await websocket.send_text(json.dumps({"status": "success", "message": message_data['message']}))
      await manager.broadcast(websocket, data)
  except WebSocketDisconnect:
        await manager.disconnect(websocket)
