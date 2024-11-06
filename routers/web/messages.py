
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from data.models.user import UserAuthDep
from services import messages_services


message_router = APIRouter(prefix='/messages', tags=['Messages'])
templates = Jinja2Templates(directory="templates")

@message_router.get('/', response_class=HTMLResponse)
def message_page(request: Request, current_user: UserAuthDep = Depends()):

    messages = [ 
        { "message_id": 1, "text": "Hello", "sender_id": current_user.user_id, "receiver_id": 2 },
        { "message_id": 2, "text": "Hi", "sender_id": 2, "receiver_id": current_user.user_id }
     ]
    
    return templates.TemplateResponse("messages.html", {"request": request, "messages": messages})


@message_router.post('/send', response_class=HTMLResponse)
def send_message(receiver_id: int = Form(...), text: str = Form(...), current_user: UserAuthDep = Depends()):
    if not text.strip():
        return templates.TemplateResponse("error.html", {"message": "Message cannot be empty"})

    messages_services.create_message(text, current_user.user_id, receiver_id)
    return templates.TemplateResponse("success.html", {"message": "Message sent"})


@message_router.get('/api/messages/{receiver_id}', response_model=None)
def get_user_messages(receiver_id: int, current_user: UserAuthDep = Depends()):
    messages = messages_services.get_messages(current_user.user_id, receiver_id)

    return messages