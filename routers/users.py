from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from common.responses import BadRequest, Forbidden
from data.models.user import TokenResponse, User, UserLogin, UserResponse
from services import users_services
from services.users_services import oauth2_scheme



users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.post('/register',  response_model= UserResponse)
def register_user (user: UserLogin):
    if users_services.get_user(user.username):
        return BadRequest('User already exists') 
    
    hashed_password = users_services.get_password_hash(user.password) 
    user.password = hashed_password
    user_id = users_services.create_user(user)
    if user_id:
        user.id = user_id
        return user
    else:
        return BadRequest('User creation failed')


@users_router.post('/login', response_model= TokenResponse)
def login_user(data: OAuth2PasswordRequestForm = Depends()):
    user = users_services.login_user(data.username, data.password)
    is_admin = user.is_admin
    id = user.id
    if not user:
        return BadRequest('Invalid username or password')
    access_token = users_services.create_access_token(data={'sub': user.username, 'is_admin': is_admin, "id": id})
    return TokenResponse(access_token=access_token, token_type='bearer')


@users_router.get('/me', response_model= UserResponse)
def get_current_user(user: User = Depends(users_services.get_current_user)):
    return user



@users_router.post('/logout')
def lougout_user(token: str = Depends(oauth2_scheme)):
    users_services.verify_token(token)
    users_services.token_blacklist.add(token)
    return 'Logged out successfully'
    


@users_router.get('/', response_model=list[UserResponse])
def get_all_users(admin: User = Depends(users_services.get_current_admin_user)):
    return users_services.get_users()
