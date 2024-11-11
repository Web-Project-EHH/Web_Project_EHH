from fastapi import APIRouter, Request
from common.template_config import CustomJinja2Templates
import common.auth
from services import topics_services


router = APIRouter(prefix='', tags=['Homepage'])
templates = CustomJinja2Templates(directory="templates")

@router.get('/', response_model=None)
def serve_homepage(request: Request = None):
    token = request.cookies.get('token')
    current_user = common.auth.get_current_user(token)
    topics = topics_services.fetch_all_topics(per_page=100, current_user=current_user)
    return templates.TemplateResponse(name='index.html', request=request, context={'token': token, 'topics': topics})   