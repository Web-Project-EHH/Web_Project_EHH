from data.models.message import Message
from data.models.user import UserInfo
from data.database import read_query, insert_query, update_query

def exists(message_id):
    return any(read_query('''SELECT * FROM messages WHERE id = ?''', (message_id,)))

def create_message(message_text, sender_id, receiver_id):
    return insert_query('''INSERT INTO messages (message_text, sender_id, receiver_id) VALUES (?, ?, ?)''', (message_text, sender_id, receiver_id))

def get_messages(sender_id: int, receiver_id: int):
    data = read_query('''SELECT * FROM messages WHERE sender_id = ? AND receiver_id = ?
    ORDER BY message_id ASC''',
    (sender_id, receiver_id))

    return [Message.from_query(row) for row in data]

def get_all_messages(user_id: int):
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
    
    return [UserInfo.from_query(row) for row in data]

def update_message(message_id, message_text):
    return update_query('''UPDATE messages SET message_text = ? WHERE message_id = ?''', (message_text, message_id))