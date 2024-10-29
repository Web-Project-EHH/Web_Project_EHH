from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix='/home', tags=['Homepage'])
templates = Jinja2Templates(directory="templates")

@router.get('/', response_model=None)
def serve_homepage(request: Request = None):
    return templates.TemplateResponse(name='index.html', request=request)