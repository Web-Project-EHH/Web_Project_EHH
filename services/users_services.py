from fastapi import Form
from common.exceptions import NotFoundException
from data.models.user import User, UserProfileUpdate, UserRegistration, UserResponse
from services import replies_services
from data.database import read_query, insert_query, update_query
from data.models.vote import Vote
import common.auth
from mariadb import IntegrityError


def create_user(user: User) -> int:
    return insert_query(
        'INSERT INTO users (username, password, email, first_name, last_name) VALUES (?, ?, ?, ?, ?)',
        (user.username, user.password, user.email, user.first_name, user.last_name)
    )


def get_user(username: str) -> UserResponse:
    data = read_query(
        '''SELECT user_id, username, password, email, first_name, 
           last_name, is_admin, is_deleted, bio 
           FROM users WHERE username = ?''',
        (username,)
    )
    if not data:
        return None
        
    user_dict = {
        'id': data[0][0],
        'username': data[0][1],
        'password': data[0][2],
        'email': data[0][3],
        'first_name': data[0][4],
        'last_name': data[0][5],
        'is_admin': bool(data[0][6]),
        'is_deleted': bool(data[0][7]),
        'bio': data[0][8]
    }
    
    return UserResponse(**user_dict)

def get_user_by_id(user_id: int) -> User | None:
    """Get user by ID with all fields including bio"""
    data = read_query(
        '''SELECT user_id as id, username, password, email, first_name, 
           last_name, is_admin, is_deleted, bio 
           FROM users WHERE user_id = ?''',
        (user_id,)
    )
    
    if not data:
        return None
        
    user_dict = {
        'id': data[0][0],
        'username': data[0][1], 
        'password': data[0][2],
        'email': data[0][3],
        'first_name': data[0][4],
        'last_name': data[0][5],
        'is_admin': bool(data[0][6]),
        'is_deleted': bool(data[0][7]),
        'bio': data[0][8]
    }
    
    return User(**user_dict)


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

def get_registration(username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), email: str = Form(...), first_name: str = Form(...), last_name: str = Form(...)):
    return UserRegistration(username=username, password=password, confirm_password=confirm_password, email=email, first_name=first_name, last_name=last_name, is_admin=False)


def email_exists(email: str) -> bool:
    user = read_query('''SELECT email FROM users WHERE email = ?''', (email,))
    return bool(user)

def get_users_by_username(username: str):
    data = read_query('SELECT * FROM users WHERE username LIKE ?', (f'%{username}%',))
    return [UserResponse.from_query_result(row) for row in data]

def delete_user(user_id: int):
    return insert_query('DELETE FROM users WHERE user_id = ?', (user_id,))

def check_user_access_level(user_id: int, category_id: int) -> int:
    data = read_query('SELECT write_access FROM users_categories_permissions WHERE user_id = ? AND category_id = ?', (user_id, category_id))
    if not data:
        return 2
    return data[0][0]

def update_user_permissions(user_id: int, category_id: int, access_level: int):
    has_entry = read_query('SELECT * FROM users_categories_permissions WHERE user_id = ? AND category_id = ?', (user_id, category_id))

    if not has_entry:
        return insert_query('INSERT INTO users_categories_permissions (user_id, category_id, write_access) VALUES (?, ?, ?)', (user_id, category_id, access_level))

    return insert_query('UPDATE users_categories_permissions SET write_access = ? WHERE user_id = ? AND category_id = ?', (access_level, user_id, category_id))

def update_user_profile(user_id: int, email: str, first_name: str, last_name: str, bio: str = None, new_password: str = None, confirm_password: str = None):
    """Updates user profile information"""
    try:
        if new_password:
            if not confirm_password:
                raise ValueError("Please confirm your new password")
            if new_password != confirm_password:
                raise ValueError("Passwords do not match")
            
            hashed_password = common.auth.get_password_hash(new_password)
            update_query(
                '''UPDATE users 
                   SET email = ?, first_name = ?, last_name = ?, password = ?, bio = ? 
                   WHERE user_id = ?''',
                (email, first_name, last_name, hashed_password, bio, user_id)
            )
        else:
            update_query(
                '''UPDATE users 
                   SET email = ?, first_name = ?, last_name = ?, bio = ? 
                   WHERE user_id = ?''',
                (email, first_name, last_name, bio, user_id)
            )
    except IntegrityError:
        raise ValueError("Email address already in use")