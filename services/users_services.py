from common.exceptions import NotFoundException
from data.models.user import User, UserResponse
from services import replies_services
from data.database import read_query, insert_query
from data.models.vote import Vote

    
def create_user(user: User) -> int:
    return insert_query(
        'INSERT INTO users (username, password, email, first_name, last_name) VALUES (?, ?, ?, ?, ?)',
        (user.username, user.password, user.email, user.first_name, user.last_name)
    )



def get_user(username: str) -> UserResponse:
    data = read_query( 'SELECT * FROM users WHERE username=?',(username,))
    if not data:
        return None
    return UserResponse.from_query_result(data[0])



def get_users():
    data = read_query('SELECT * FROM users')
    return [UserResponse.from_query_result(row) for row in data]
    


def has_voted(user_id: int, reply_id: int) -> Vote | None:
    
    """
    Checks if a user has voted on a specific reply.

    Args:
        user_id (int): The ID of the user.
        reply_id (int): The ID of the reply.

    Returns:
        Vote | None: A Vote object if the user has voted on the reply, otherwise None.

    Raises:
        NotFoundException: If the user or the reply does not exist.
    """

    if not exists(user_id):
        raise NotFoundException(detail='User does not exist')
    
    if not replies_services.exists(reply_id):
        raise NotFoundException(detail='Reply does not exist')
    
    vote = read_query('''SELECT user_id, reply_id, type FROM votes WHERE user_id = ? AND reply_id = ?''', (user_id, reply_id))

    return next((Vote.from_query_result(*row) for row in vote), None)


def exists(user_id: int) -> bool:
    
    user = read_query('''SELECT user_id FROM users WHERE user_id = ?''', (user_id,))

    return bool(user)

UserAuthDep =  Annotated[User, Depends(get_current_user)]

def hash_existing_user_passwords():
    users = read_query('SELECT user_id, password FROM users')
    
    for user_id, plain_password in users:
        if len(plain_password) != 60:
            hashed_password = get_password_hash(plain_password)
            
            insert_query('UPDATE users SET password = ? WHERE user_id = ?', (hashed_password, user_id))
    
    print("All user passwords have been hashed successfully.")