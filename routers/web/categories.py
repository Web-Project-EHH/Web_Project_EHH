import math
from fastapi.responses import JSONResponse, RedirectResponse
import common.auth
from common.template_config import CustomJinja2Templates
from data.models.user import User
from services import categories_services, users_services
from fastapi import APIRouter, Depends, Request
from common.exceptions import BadRequestException
from data.models.category import CategoryChangeName, CategoryChangeNameID, CategoryCreate
from fastapi import Query
from typing import Literal, Optional


router = APIRouter(prefix='/categories', tags=['Categories'])
templates = CustomJinja2Templates(directory="templates")

@router.get('/create', response_model=None)
def create_category_page(request: Request):
    return templates.TemplateResponse(name='create-category.html', request=request)

@router.get('/', response_model=None)
def get_categories(category_id: Optional[int] = Query(default=None), 
                   name: Optional[str] = Query(default=None), 
                   sort_by: Literal["name", "category_id"] | None = Query(default='name'), 
                   sort: Literal["asc", "desc",] | None = Query(default='asc'),
                   limit: int = Query(default=15, ge=1),
                   offset: int = Query(default=0, ge=0), request: Request = None,
                   page: int = Query(default=1, ge=1)):
    
    
    current_user = common.auth.get_current_user(request.cookies.get('token'))

    if not current_user:
        return templates.TemplateResponse(name='categories.html', context={'error': 'You need to login to view this page'}, request=request)

    token = request.cookies.get('token')
    current_user = common.auth.get_current_user(token)
    offset = (page-1) * limit
    total_categories = len(categories_services.get_categories(current_user, limit=10000))
    print(total_categories)
    total_pages = math.ceil(total_categories / limit)

    
    categories = categories_services.get_categories(category_id=category_id,name=name,sort_by=sort_by,sort=sort,
                                                        limit=limit, offset=offset, current_user=current_user)
    if page > total_pages and total_categories > 0:
        return templates.TemplateResponse(name='categories.html', context={'error': 'Page not found'}, request=request)
    
    if not categories:
        return templates.TemplateResponse(name='categories.html', context={'error': 'No matching categories found'}, request=request)
    
    return templates.TemplateResponse(name='categories.html', context={'categories': categories, 'page': page, 'total_pages': total_pages, 'limit': limit}, request=request) 


@router.get('/{category_id}', response_model=None)
def get_category_by_id(category_id: int, request: Request = None):

    current_user = common.auth.get_current_user(request.cookies.get('token'))

    per_page = 10

    if not current_user:
        return templates.TemplateResponse(name='categories.html', context={'error': 'You need to login to view this page'}, request=request)


    category_data = categories_services.get_by_id(category_id=category_id, current_user=current_user)

    if category_data is None:
        return templates.TemplateResponse(name='categories.html', context={'error': 'Category not found'}, request=request)

    topics = category_data['Topics']

    category = category_data['Category']

    if category.is_private and not current_user.is_admin: 
        if not users_services.check_user_access_level(user_id=current_user.id, category_id=category_id) > 0 :
            return templates.TemplateResponse(name='categories.html', context={'error': 'Not authorised to see this category'}, request=request)

    if not category:
        return templates.TemplateResponse(name='categories.html', context={'error': 'Category not found'}, request=request)
    
    return templates.TemplateResponse(name='single-category.html', context={'category': category, 'topics': topics, 'per_page': per_page}, request=request)


@router.post('/create', response_model=None)
def create_category(category: CategoryCreate = Depends(categories_services.category_create_form), request: Request = None):

    user = common.auth.get_current_user(request.cookies.get('token'))
    
    if not user.is_admin:
        return templates.TemplateResponse(name='categories.html', context={'error': 'User not authorised'}, request=request)

    new_category = categories_services.create(category)

    return RedirectResponse(url=f"/categories/{new_category.id}", status_code=303)


@router.patch('/', response_model=None)
def update_category_name(old_category:CategoryChangeNameID, new_category: CategoryChangeName, 
                         admin: User = Depends(common.auth.get_current_admin_user), request: Request = None):
    
    updated = categories_services.update_name(old_category, new_category)

    return templates.TemplateResponse(name='single-category.html', context={'category': updated}, request=request)


@router.patch('/{category_id}/lock', response_model=None)
def lock_unlock_category(category_id: int, request: Request = None):

    user = common.auth.get_current_user(request.cookies.get('token'))

    if not user.is_admin:
        return templates.TemplateResponse(name='categories.html', context={'error': 'User not authorised'}, request=request)
    category = categories_services.get_by_id(category_id=category_id, current_user=user)

    if not category:
        return templates.TemplateResponse(name='categories.html', context={'error': 'Category not found'}, request=request)
        
    result = categories_services.lock_unlock(category_id)

    if result == 'locked':
        return JSONResponse({'message': 'Category locked'}, status_code=200)
    
    elif result == 'unlocked':
        return JSONResponse({'message': 'Category unlocked'}, status_code=200)

    elif result == 'lock failed':
        raise BadRequestException(detail='Category could not be locked')
    
    elif result == 'unlock failed':
        raise BadRequestException(detail='Category could not be unlocked')
    

@router.patch('/{category_id}/make_private', response_model=None)
def make_category_private(category_id: int, request: Request = None):

    user = common.auth.get_current_user(request.cookies.get('token'))

    if not user.is_admin:
        return templates.TemplateResponse(name='categories.html', context={'error': 'User not authorised'}, request=request)

    result = categories_services.privatise_unprivatise(category_id)

    if not result:
        raise BadRequestException(detail='Operation failed')

    elif result == 'made private':
        return JSONResponse({'message': 'Category made private'}, status_code=200)
        
    elif result == 'made public':
        return JSONResponse({'message': 'Category made public'}, status_code=200)

    elif result == 'made private failed':
        raise BadRequestException(detail='Category could not be made private')
        
    elif result == 'made public failed':
        raise BadRequestException(detail='Category could not be made public')


@router.delete('/{category_id}', response_model=None)
async def delete_category(category_id: int, request: Request = None):

    user = common.auth.get_current_user(request.cookies.get('token'))

    if not user.is_admin:
        return templates.TemplateResponse(name='categories.html', context={'error': 'User not authorised'}, request=request)

    payload = await request.json()

    delete_topics = payload.get('delete_topics', False)

        
    result = categories_services.delete(category_id, delete_topics)
    
    if not result:
        raise BadRequestException(detail='Category could not be deleted')

    elif result == 'everything deleted':
        return JSONResponse({'message': 'Category and topics deleted'}, status_code=200)
            
    elif result == 'only category deleted':
        return JSONResponse({'message': 'Category deleted'}, status_code=200)
            
    # except IntegrityError:
    #     raise ForbiddenException(detail='Cannot delete a category that includes topics.')