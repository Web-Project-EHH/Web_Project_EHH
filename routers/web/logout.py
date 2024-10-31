from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from common import auth
from common.responses import BadRequest, Forbidden
from data.models.user import TokenResponse, User, UserLogin, UserResponse
from services import users_services
from common.auth import oauth2_scheme
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix='/logout', tags=['Logout'])
templates = Jinja2Templates(directory="templates")

@router.post('/')
def logout_user(token: str = Depends(oauth2_scheme), request: Request = None):
    auth.verify_token(token)
    auth.token_blacklist.add(token)
    return templates.TemplateResponse(name='index.html', context={'message': 'Logged out successfully'}, request=request)