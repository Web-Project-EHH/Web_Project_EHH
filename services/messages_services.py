from data.models.message import Message
from data.models.user import UserInfo
from data.database import read_query, insert_query, update_query
from services.users_services import UserAuthDep
from fastapi import HTTPException


#WORKS
def exists(message_id: int):
    """
    Check if a message exists in the database
    Parameters:
    message_id: int
    Returns:
    bool
    """
    return any(read_query('''SELECT * FROM messages WHERE message_id = ?''', (message_id,)))


#WORKS
def create_message(message_text: str, sender_id: int, receiver_id: int):
    """
    Create a new message in the database
    Parameters:
    message_text: str
    sender_id: int
    receiver_id: int
    """
    return insert_query('''INSERT INTO messages (text, sender_id, receiver_id) VALUES (?, ?, ?)''', (message_text, sender_id, receiver_id))


#WORKS
def get_conversation(user_id: int, receiver_id: int):
    """
    Get all messages between two users
    Parameters:
    user_id: int
    receiver_id: int
    Returns:
    all messages between the two users
    """
    data = read_query('''SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?) 
                         OR (sender_id = ? AND receiver_id = ?)
                         ORDER BY message_id ASC''',
    (user_id, receiver_id, receiver_id, user_id))

    return [Message.from_query(row) for row in data]


#WORKS
def get_all_conversations(user_id: int):
    """
    Get all conversations for a user
    Parameters:
    user_id: int
    Returns:
    all users that the user has exchanged messages with
    """
    data = read_query('''SELECT u.username, u.email, u.first_name, u.last_name
                      FROM users u
                      JOIN messages m
                      ON u.user_id = m.receiver_id
                      WHERE m.sender_id = ?
                      UNION
                      SELECT u.username, u.email, u.first_name, u.last_name
                      FROM users u
                      JOIN messages m
                      ON u.user_id = m.sender_id
                      WHERE m.receiver_id = ?''', (user_id, user_id))
    
    return [UserInfo.from_query_result(*row) for row in data]


#WORKS
def update_message(message_id: int, text: str, current_user: UserAuthDep):
    """
    Update a message in the database if the user is the sender
    Parameters:
    message_id: int
    text: str
    current_user: UserAuthDep
    Returns:
    message edited successfully or raises an exception
    """
    if not exists(message_id):
        raise HTTPException(status_code=404, detail='Message does not exist')

    if not text:
        raise HTTPException(status_code=400, detail='Message cannot be empty')
    
    if not read_query('''SELECT * FROM messages WHERE message_id = ? AND sender_id = ?''', (message_id, current_user.id)):
        raise HTTPException(status_code=403, detail='You cannot edit this message')
    
    update_query('''UPDATE messages SET text = ? WHERE message_id = ?''', (text, message_id))

    return {"detail": "Message updated successfully"}
 