import common.auth
from common.template_config import CustomJinja2Templates
from data.models.user import User
from services import categories_services
from fastapi import APIRouter, Depends, Request
from common.exceptions import BadRequestException, ForbiddenException
from data.models.category import CategoryChangeName, CategoryChangeNameID, CategoryCreate
from fastapi import Query
from typing import Literal, Optional
from mariadb import IntegrityError


router = APIRouter(prefix='/categories', tags=['Categories'])
templates = CustomJinja2Templates(directory="templates")

@router.get('/', response_model=None)
def get_categories(category_id: Optional[int] = Query(default=None), 
                   name: Optional[str] = Query(default=None), 
                   sort_by: Literal["name", "category_id"] | None = Query(default=None), 
                   sort: Literal["asc", "desc",] | None = Query(default=None),
                   limit: int = Query(default=10, ge=1),
                   offset: int = Query(default=0, ge=0), request: Request = None):

    token = request.cookies.get('token')
    current_user = common.auth.get_current_user(token)

    categories = categories_services.get_categories(category_id=category_id,name=name,sort_by=sort_by,sort=sort,
                                                        limit=limit, offset=offset, current_user=current_user)
    
    
    
    return templates.TemplateResponse(name='categories.html', context={'categories': categories, 'token': token}, request=request) 


@router.get('/{id}', response_model=None)
def get_category_by_id(category_id: int, current_user: User=Depends(common.auth.get_current_user), request: Request = None):

    category = categories_services.get_by_id(category_id=category_id, current_user=current_user)

    token = request.cookies.get('token')
    
    return templates.TemplateResponse(name='single-category.html', context={'category': category, 'token': token}, request=request)


@router.post('/', response_model=None)
def create_category(category: CategoryCreate, admin: User = Depends(common.auth.get_current_admin_user), request: Request = None):

    new_category = categories_services.create(category)

    token = request.cookies.get('token')

    return templates.TemplateResponse(name='single-category.html', context={'category': new_category, 'token': token}, request=request)


@router.patch('/', response_model=None)
def update_category_name(old_category:CategoryChangeNameID, new_category: CategoryChangeName, 
                         admin: User = Depends(common.auth.get_current_admin_user), request: Request = None):
    
    updated = categories_services.update_name(old_category, new_category)

    return templates.TemplateResponse(name='single-category.html', context={'category': updated}, request=request)


@router.patch('/{category_id}/lock', response_model=None)
def lock_unlock_category(category_id: int, admin: User = Depends(common.auth.get_current_admin_user), request: Request = None):

    result = categories_services.lock_unlock(category_id)

    if not result:
        raise BadRequestException(detail='Operation failed')

    elif result == 'locked':
        return templates.TemplateResponse(name='single-category.html', context={'category': 'Category locked'}, status_code=200, request=request)
    
    elif result == 'unlocked':
        return templates.TemplateResponse(name='single-category.html', context={'category': 'Category unlocked'}, status_code=200, request=request)

    elif result == 'lock failed':
        raise BadRequestException(detail='Category could not be locked')
    
    elif result == 'unlock failed':
        raise BadRequestException(detail='Category could not be unlocked')
    

@router.patch('/{category_id}/make_private', response_model=None)
def make_category_private(category_id: int, admin: User = Depends(common.auth.get_current_admin_user), request: Request = None):

    result = categories_services.privatise_unprivatise(category_id)

    if not result:
        raise BadRequestException(detail='Operation failed')

    elif result == 'made private':
        return templates.TemplateResponse(name='single-category.html', context={'category': 'Category made private'}, status_code=200, request=request)
    
    elif result == 'made public':
        return templates.TemplateResponse(name='single-category.html', context={'category': 'Category made public'}, status_code=200, request=request)

    elif result == 'made private failed':
        raise BadRequestException(detail='Category could not be made private')
    
    elif result == 'made public failed':
        raise BadRequestException(detail='Category could not be made public')


@router.delete('/', response_model=None)
def delete_category(category_id: int = Query(int), delete_topics: bool = Query(False),
                    admin: User = Depends(common.auth.get_current_admin_user), request: Request = None):

    try:
        
        result = categories_services.delete(category_id, delete_topics)
        
        if not result:
            raise BadRequestException(detail='Category could not be deleted')

        elif result == 'everything deleted':
            return templates.TemplateResponse(name='categories.html', context={'message': 'Category and topics deleted'}, status_code=200, request=request)
        
        elif result == 'only category deleted':
            return templates.TemplateResponse(name='categories.html', context={'message': 'Category deleted'}, status_code=200, request=request)
    except IntegrityError:
        raise ForbiddenException(detail='Cannot delete a category that includes topics.')