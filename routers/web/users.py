from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from common import auth
from services import users_services
from common.template_config import CustomJinja2Templates
from data.models.user import UserRegistration

router = APIRouter(prefix='/users', tags=['User'])
templates = CustomJinja2Templates(directory="templates")


@router.get('/', response_model=None)
def serve_users(request: Request):

    user = auth.get_current_user(request.cookies.get('token'))

    if not user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'You need to login to view this page'})
    
    return templates.TemplateResponse(name="users.html", request=request)


@router.get('/register', response_model=None)
def serve_register (request: Request):
    return templates.TemplateResponse(name="register.html", request=request)


@router.post('/register', response_model=None)
def register_user(request: Request = None, register: UserRegistration = Depends(users_services.get_registration)):
    if users_services.get_user(register.username):
        return templates.TemplateResponse(name="register.html", request=request, context={'error': 'User already exists'})

    if users_services.email_exists(register.email):
        return templates.TemplateResponse(name="register.html", request=request, context={'error': 'Email already exists'})

    if register.password != register.confirm_password:
        return templates.TemplateResponse(name="register.html", request=request, context={'error': 'Passwords do not match'})
    
    hashed_password = auth.get_password_hash(register.password) 
    register.password = hashed_password
    user_id = users_services.create_user(register)
    response = RedirectResponse(url='/', status_code=302)
    response.set_cookie('token', auth.create_access_token(data={'sub': register.username, 'is_admin': False, "id": user_id}))
    return response
    

@router.get('/login', response_model=None)
def serve_login(request: Request):
    return templates.TemplateResponse(name="login.html", request=request)


@router.post('/login', response_model=None)
def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    user = auth.authenticate_user(form_data.username, form_data.password)

    if not user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'Invalid username or password'})
    
    is_admin = user.is_admin
    id = user.id

    access_token = auth.create_access_token(data={'sub': user.username, 'is_admin': is_admin, "id": id})
    response = RedirectResponse(url='/', status_code=302)
    response.set_cookie('token', access_token)
    return response


@router.post('/logout')
def logout(request: Request = None):
    token = request.cookies.get('token')
    auth.token_blacklist.add(token)
    response = RedirectResponse(url='/', status_code=302)
    response.delete_cookie('token')
    return response


@router.get('/me', response_model=None)
def get_current_user_me(request: Request = None):
    return templates.TemplateResponse(name="profile.html", request=request)

@router.get('/search', response_model=None)
def search_users(request: Request, username: str = Query(...)):

    current_user = auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'You need to login to view this page'})

    users = users_services.get_users_by_username(username)
    return templates.TemplateResponse(request=request, name="users.html", context={'users': users})

@router.get('/{user_id}', response_model=None)
def get_user_by_id(user_id: int, request: Request = None):

    current_user = auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse(name="login.html", request=request, context={'error': 'You need to login to view this page'})

    user = users_services.get_user_by_id(user_id)
    return templates.TemplateResponse(name="user_profile.html", request=request, context={'user': user})