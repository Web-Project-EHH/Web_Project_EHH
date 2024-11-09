from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from common.exceptions import BadRequestException
from data.models.user import User, UserLogin, UserResponse, TokenResponse
import common.auth as auth
from services import users_services
from common.auth import oauth2_scheme


users_router = APIRouter(prefix='/api/users', tags=['Users'])


@users_router.post('/register',  response_model= UserResponse)
def register_user (user: UserLogin):
    if users_services.get_user(user.username):
        return BadRequestException('User already exists') 

    hashed_password =  auth.get_password_hash(user.password) 
    user.password = hashed_password
    user_id = users_services.create_user(user)
    if user_id:
        user.id = user_id
        return user
    else:
        return BadRequestException('User creation failed')


@users_router.post('/login', response_model= TokenResponse)
def login_user(data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(data.username, data.password)
    if not user:
        return BadRequestException('Invalid username or password')
    is_admin = user.is_admin
    id = user.id
    access_token = auth.create_access_token(data={'sub': user.username, 'is_admin': is_admin, "id": id})

    return TokenResponse(access_token=access_token, token_type='bearer')


@users_router.get('/me', response_model= UserResponse)
def get_current_user(user: User = Depends(auth.get_current_user)):
    return user


@users_router.post('/logout')
def lougout_user(token: str = Depends(oauth2_scheme)):
    auth.verify_token(token)
    auth.token_blacklist.add(token)
    return 'Logged out successfully'


@users_router.get('/', response_model=list[UserResponse])
def get_all_users(admin: User = Depends(auth.get_current_admin_user)):
    return users_services.get_users()