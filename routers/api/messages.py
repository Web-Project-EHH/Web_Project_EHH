from fastapi import APIRouter, HTTPException
from data.models.message import MessageText
from services import messages_services, users_services
from common.auth import UserAuthDep
from data.database import read_query

#DA OPRAVQ EXCEPTIONITE  !

messages_router = APIRouter(prefix='/api/messages', tags=['messages'])

#WORKS
@messages_router.post('/{receiver_id}', status_code=201)
def send_message(receiver_id: int, message: MessageText, current_user: UserAuthDep):
    """
    Send a message to a user with the given receiver_id
    Parameters:
    receiver_id: int
    message: MessageText
    current_user: UserAuthDep
    Returns:
    str: Message sent to {receiver_username}
    """
    if not message.text:
        raise HTTPException(status_code=400, detail='Message cannot be empty')

    receiver = users_services.exists(receiver_id)
    if not receiver :
        raise HTTPException(status_code=404, detail='Receiver does not exist')
    
    messages_services.create_message(message.text, current_user.id, receiver_id)
    receiver_username = read_query('''SELECT username FROM users WHERE user_id = ?''', (receiver_id,))[0][0]
    return f'Message sent to {receiver_username}'

#WORKS
@messages_router.get('/{receiver_id}')
def get_messages(receiver_id: int, current_user: UserAuthDep):
    """
    Get all messages between the current user and the user with the given receiver_id
    Parameters:
    receiver_id: int
    current_user: UserAuthDep
    Returns:
    All messages between the current user and the user with the given receiver_id
    """
    if not users_services.exists(receiver_id):
        raise HTTPException(status_code=404, detail='User does not exist')
    
    messages = messages_services.get_conversation(current_user.id, receiver_id)
    return messages or 'No messages found'

#WORKS
@messages_router.get('/convesations/all')
def get_all_conversations(current_user: UserAuthDep):
    """
    Get all conversations of the current user
    Parameters:
    current_user: UserAuthDep
    Returns:
    All conversations of the current user
    """
    messages = messages_services.get_all_conversations(current_user.id)
    return messages or 'No messages found'


@messages_router.patch('/{message_id}')
def edit_message(message_id: int, message: MessageText, current_user: UserAuthDep):
    """
    Edit a message with the given message_id
    Parameters:
    message_id: int
    message: MessageText
    current_user: UserAuthDep
    Returns:
    str: Message edited successfully
    """
    if not messages_services.exists(message_id):
        raise HTTPException(status_code=404, detail='Message does not exist')
    
    message = messages_services.update_message(message_id, message.text, current_user)
    return 'Message edited successfully'