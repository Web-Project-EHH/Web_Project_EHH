from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from common import auth
from common.exceptions import BadRequestException
from common.responses import BadRequest
from data.models.user import UserLogin
from services import users_services
from common.template_config import CustomJinja2Templates

router = APIRouter(prefix='/users', tags=['User'])
templates = CustomJinja2Templates(directory="templates")


@router.get('/register', response_model=None)
def serve_register (request: Request):
    return templates.TemplateResponse(name="register.html", request=request)

@router.post('/register', response_model=None)
def register_user(user: UserLogin, request: Request = None):
    if users_services.get_user(user.username):
        return BadRequest('User already exists') 
    
    hashed_password = auth.get_password_hash(user.password) 
    user.password = hashed_password
    user_id = users_services.create_user(user)
    user.id = user_id
    response = RedirectResponse(url='/', status_code=302)
    response.set_cookie('token', auth.create_access_token(data={'sub': user.username, 'is_admin': user.is_admin, "id": user.id}))
    return response
    

@router.get('/login', response_model=None)
def serve_login(request: Request):
    return templates.TemplateResponse(name="login.html", request=request)


@router.post('/login', response_model=None)
def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    user = auth.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise BadRequestException(detail='Invalid username or password')
    
    is_admin = user.is_admin
    id = user.id

    access_token = auth.create_access_token(data={'sub': user.username, 'is_admin': is_admin, "id": id})
    response = RedirectResponse(url='/home', status_code=302)
    response.set_cookie('token', access_token)
    return response


@router.post('/logout')
def logout(request: Request = None):
    token = request.cookies.get('token')
    auth.verify_token(token)
    auth.token_blacklist.add(token)
    response = RedirectResponse(url='/home', status_code=302)
    response.delete_cookie('token')
    return response


