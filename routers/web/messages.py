
from dataclasses import dataclass
from datetime import datetime
import json
import uuid
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services import messages_services
from services.messages_services import create_message



router = APIRouter(prefix='/messages', tags=['Messages'])
templates = Jinja2Templates(directory="templates")


@dataclass
class ConnectionManager:

  """
    Manages WebSocket connections.

    Attributes:
        active_connections (dict): A dictionary of active WebSocket connections.
  """

  def __init__(self) -> None:
    """
    Initializes the ConnectionManager with an empty dictionary of active connections.
    """
    self.active_connections: dict = {}

  async def connect(self, websocket: WebSocket):

    """
    Accepts a new WebSocket connection and adds it to the active connections.

    Args:
        websocket (WebSocket): The WebSocket connection to add.
    """
    await websocket.accept()
    id = str(uuid.uuid4())
    self.active_connections[id] = websocket

    await self.send_message(websocket, json.dumps({"isMe": True, "data": "Have joined!!", "username": "You", "time": datetime.now().strftime('%H:%M:%S')}))

  async def send_message(self, ws: WebSocket, message: str):

    """
    Sends a message to a specific WebSocket connection.

    Args:
        ws (WebSocket): The WebSocket connection to send the message to.
        message (str): The message to send.
    """
    await ws.send_text(message)

  def find_connection_id(self, websocket: WebSocket):

    """
    Finds the connection ID for a given WebSocket connection.

    Args:
        websocket (WebSocket): The WebSocket connection to find the ID for.

    Returns:
        str: The connection ID.
    """
    websocket_list = list(self.active_connections.values())
    id_list = list(self.active_connections.keys())

    pos = websocket_list.index(websocket)
    return id_list[pos]

  async def broadcast(self, webSocket: WebSocket, data: str):

    """
    Broadcasts a message to all active WebSocket connections.

    Args:
        webSocket (WebSocket): The WebSocket connection that sent the message.
        data (str): The message data to broadcast.
    """
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

    """
    Disconnects a WebSocket connection and removes it from the active connections.

    Args:
        websocket (WebSocket): The WebSocket connection to disconnect.

    Returns:
        str: The ID of the disconnected connection.
    """
    id = self.find_connection_id(websocket)
    del self.active_connections[id]

    return id


manager = ConnectionManager()


@router.get("/", response_class=HTMLResponse)
def get_room(request: Request):

  """
  Renders the chat room HTML page.

  Args:
      request (Request): The request object.

  Returns:
      TemplateResponse: The rendered HTML page.
  """
  return templates.TemplateResponse("message.html", {"request": request})

@router.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):

  """
    Handles WebSocket connections for the chat room.

    Args:
        websocket (WebSocket): The WebSocket connection.

    Raises:
        WebSocketDisconnect: If the WebSocket connection is disconnected.
    """
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
