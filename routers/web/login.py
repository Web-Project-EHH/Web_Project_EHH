from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from common import auth
from common.responses import BadRequest, Forbidden
from data.models.user import TokenResponse, User, UserLogin, UserResponse

from fastapi.templating import Jinja2Templates


router = APIRouter(prefix='/login', tags=['Login'])
templates = Jinja2Templates(directory="templates")

@router.get('/', response_model=None)
def show_login_form(request: Request):
    return templates.TemplateResponse(name="login.html", request=request)

@router.post('/', response_model=None)
def login_user(data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    user = auth.authenticate_user(data.username, data.password)
    is_admin = user.is_admin
    id = user.id
    if not user:
        return BadRequest('Invalid username or password')
    access_token = auth.create_access_token(data={'sub': user.username, 'is_admin': is_admin, "id": id})

    return templates.TemplateResponse(name='single-user.html', context={'token': access_token}, request=request)

