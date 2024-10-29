from fastapi import APIRouter, Request
from common import auth
from common.responses import BadRequest
from data.models.user import UserLogin
from services import users_services
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix='/register', tags=['Register'])
templates = Jinja2Templates(directory="templates")

@router.get('/', response_model=None)
def show_register_form(request: Request):
    return templates.TemplateResponse(name="register.html", request=request)

@router.post('/', response_model=None)
def register_user (user: UserLogin, request: Request = None):
    if users_services.get_user(user.username):
        return BadRequest('User already exists') 
    
    hashed_password =  auth.get_password_hash(user.password) 
    user.password = hashed_password
    user_id = users_services.create_user(user)
    if user_id:
        user.id = user_id
        return templates.TemplateResponse(name='register.html', context={'user': user}, request=request)
    else:
        return templates.TemplateResponse(name='error.html', context={'message': 'An error occurred'}, request=request)
