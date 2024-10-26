from datetime import timedelta, datetime
from typing import Optional
from fastapi import Depends
from jose import JWTError, jwt
from common.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from data.models.user import User, UserResponse
from common.exceptions import NotFoundException
from services import replies_services
from data.database import read_query
from data.models.vote import Vote
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login', auto_error=False)
token_blacklist = set()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    if token in token_blacklist:
        raise ForbiddenException("Token has been revoked")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise username
        return payload
    except JWTError:
            raise UnauthorizedException("Could not validate credentials")

    
def create_user(user: User) -> int:
    return insert_query(
        'INSERT INTO users (username, password, email, first_name, last_name) VALUES (?, ?, ?, ?, ?)',
        (user.username, user.password, user.email, user.first_name, user.last_name)
    )


def authenticate_user(username: str, password: str) -> Optional[UserResponse]:
    user_data = read_query('SELECT * FROM users WHERE username=?', (username,))
    
    if not user_data or not verify_password(password, user_data[0][2]):
        return None
    return UserResponse.from_query_result(user_data[0])


def get_user(username: str) -> UserResponse:
    data = read_query( 'SELECT * FROM users WHERE username=?',(username,))
    if not data:
        return None
    return UserResponse.from_query_result(data[0])


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    username = payload.get('sub')
    if not username:
        raise UnauthorizedException('Could not validate credentials')
    return get_user(username)

def get_current_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise ForbiddenException('You do not have permission to access this')
    return user


def get_users():
    data = read_query('SELECT * FROM users')
    return [UserResponse.from_query_result(row) for row in data]
    


# def get_user_by_id(user_id: int) -> User:
#     data = read_query('SELECT * FROM users WHERE user_id=?', (user_id,))
#     if not data:
#         return None
#     return User.from_query_result(*data[0])

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