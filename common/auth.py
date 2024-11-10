from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from common.exceptions import ForbiddenException
from data.models.user import User, UserResponse
from data.database import insert_query, read_query
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from services.users_services import get_user


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login', auto_error=False)
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

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub') if payload else None
        if username is None:
            return None
        return payload
    except JWTError:
            return None

def authenticate_user(username: str, password: str) -> Optional[UserResponse]:
    user_data = read_query('SELECT * FROM users WHERE username=?', (username,))

    if not user_data or not verify_password(password, user_data[0][2]):
        return None
    return UserResponse.from_query_result(user_data[0])


def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    payload = verify_token(token)
    username = payload.get('sub') if payload else None
    if not username:
        return None
    return get_user(username)


def get_current_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise ForbiddenException('You do not have permission to access this')
    return user

UserAuthDep =  Annotated[User, Depends(get_current_user)]

def hash_existing_user_passwords():
    users = read_query('SELECT user_id, password FROM users')
    
    for user_id, plain_password in users:
        if len(plain_password) != 60:
            hashed_password = get_password_hash(plain_password)
            
            insert_query('UPDATE users SET password = ? WHERE user_id = ?', (hashed_password, user_id))
    
    print("All user passwords have been hashed successfully.")