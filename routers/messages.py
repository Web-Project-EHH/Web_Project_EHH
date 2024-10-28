from fastapi import APIRouter, HTTPException
from common import responses
from data.models.message import MessageText
from services import messages_services, users_services
from services.users_services import UserAuthDep

#DA OPRAVQ EXCEPTIONITE I DA DOVURSHA ROUTER-A

messages_router = APIRouter(prefix='/messages', tags=['messages'])


@messages_router.post('/{receiver_id}', status_code=201)
def send_message(receiver_id: int, message: MessageText, current_user: UserAuthDep):
    if not message.text:
        raise HTTPException(status_code=400, detail='Message cannot be empty')

    receiver = users_services.get_user_by_id(receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail='Receiver does not exist')
    
    messages_services.create_message(message.text, current_user.user_id, receiver_id)
    return f'Message sent to {receiver.username}'


@messages_router.get('/{receiver_id}')
def get_messages(receiver_id: int, current_user: UserAuthDep):
    if not users_services.exists(receiver_id):
        raise HTTPException(status_code=404, detail='User does not exist')
    
    messages = messages_services.get_messages(current_user.user_id, receiver_id)
    return messages or 'No messages found'


@messages_router.get('/users')
def get_all_messages(current_user: UserAuthDep):
    messages = messages_services.get_all_messages(current_user.user_id)
    return messages or 'No messages found'


@messages_router.patch('/{message_id}')
def edit_message(message_id: int, message: MessageText, current_user: UserAuthDep):
    if not messages_services.exists(message_id):
        raise HTTPException(status_code=404, detail='Message does not exist')
    
    message = messages_services.update_message(message_id, message.text)
    return 'Message edited successfully'