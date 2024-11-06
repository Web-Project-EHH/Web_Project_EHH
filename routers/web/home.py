from fastapi import APIRouter, Request
from common.auth import get_current_user
from common.template_config import CustomJinja2Templates


router = APIRouter(prefix='', tags=['Homepage'])
templates = CustomJinja2Templates(directory="templates")

@router.get('/', response_model=None)
def serve_homepage(request: Request = None):
    token = request.cookies.get('token')
    return templates.TemplateResponse(name='index.html', request=request, context={'token': token})