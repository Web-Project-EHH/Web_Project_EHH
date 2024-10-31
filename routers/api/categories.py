from fastapi.responses import JSONResponse
from pydantic import ValidationError
import common.auth
from common import auth
from data.models.user import User
from services import categories_services, users_services
from fastapi import APIRouter, Depends, HTTPException
from common.exceptions import ConflictException, NotFoundException, BadRequestException, ForbiddenException
from data.models.category import Category, CategoryChangeName, CategoryChangeNameID, CategoryCreate, CategoryResponse
from typing import List
from fastapi import Query
from typing import Literal, Optional
from mariadb import IntegrityError


router = APIRouter(prefix='/api/categories', tags=['Categories'])


@router.get('/', response_model=None)
def get_categories(category_id: Optional[int] = Query(default=None), 
                   name: Optional[str] = Query(default=None), 
                   sort_by: Literal["name", "category_id"] | None = Query(default=None), 
                   sort: Literal["asc", "desc",] | None = Query(default=None),
                   limit: int = Query(default=10, ge=1),
                   offset: int = Query(default=0, ge=0),
                   current_user: User = Depends(common.auth.get_current_user)) -> List[CategoryResponse] | CategoryResponse:

    categories = categories_services.get_categories(category_id=category_id,name=name,sort_by=sort_by,sort=sort,
                                                        limit=limit, offset=offset, current_user=current_user)
    
    if not categories:
        raise NotFoundException(detail="No matching categories found")

    return categories


@router.get('/{id}', response_model=None)
def get_category_by_id(category_id: int, current_user: User=Depends(common.auth.get_current_user)):

    category = categories_services.get_by_id(category_id=category_id, current_user=current_user)

    if not category:
        raise NotFoundException(detail='Category not found')
    
    return category


@router.post('/', response_model=None)
def create_category(category: CategoryCreate, admin: User = Depends(common.auth.get_current_admin_user)) -> Category:


    new_category = categories_services.create(category)

    if not new_category:
        raise BadRequestException(detail="Category could not be created")

    return new_category


@router.patch('/', response_model=None)
def update_category_name(old_category:CategoryChangeNameID, new_category: CategoryChangeName, 
                         admin: User = Depends(common.auth.get_current_admin_user)) -> CategoryResponse:
    
    updated = categories_services.update_name(old_category, new_category)

    if not updated:
        raise BadRequestException(detail='Category name could not be updated')

    return updated


@router.patch('/{category_id}/lock', response_model=None)
def lock_unlock_category(category_id: int, admin: User = Depends(common.auth.get_current_admin_user)) -> JSONResponse:

    result = categories_services.lock_unlock(category_id)

    if not result:
        raise BadRequestException(detail='Operation failed')

    elif result == 'locked':
         return JSONResponse(content={'message': 'Category locked'}, status_code=200)
    
    elif result == 'unlocked':
        return JSONResponse(content={'message': 'Category unlocked'}, status_code=200)

    elif result == 'lock failed':
        raise BadRequestException(detail='Category could not be locked')
    
    elif result == 'unlock failed':
        raise BadRequestException(detail='Category could not be unlocked')
    

@router.patch('/{category_id}/make_private', response_model=None)
def make_category_private(category_id: int, admin: User = Depends(common.auth.get_current_admin_user)) -> JSONResponse:

    result = categories_services.privatise_unprivatise(category_id)

    if not result:
        raise BadRequestException(detail='Operation failed')

    elif result == 'made private':
        return JSONResponse(content={'message': 'Category made private'}, status_code=200)
    
    elif result == 'made public':
        return JSONResponse(content={'message': 'Category made public'}, status_code=200)

    elif result == 'made private failed':
        raise BadRequestException(detail='Category could not be made private')
    
    elif result == 'made public failed':
        raise BadRequestException(detail='Category could not be made public')


@router.delete('/', response_model=None)
def delete_category(category_id: int = Query(int), delete_topics: bool = Query(False),
                    admin: User = Depends(common.auth.get_current_admin_user)) -> JSONResponse:

    try:
        
        result = categories_services.delete(category_id, delete_topics)
        
        if not result:
            raise BadRequestException(detail='Category could not be deleted')

        elif result == 'everything deleted':
            return JSONResponse(content={'message': 'Category and its topics deleted'}, status_code=200)
        
        elif result == 'only category deleted':
            return JSONResponse(content={'message': 'Category deleted'}, status_code=200)

    except IntegrityError:
        raise ForbiddenException(detail='Cannot delete a category that includes topics.')
    

@router.post('/grant-read-access', response_model=None)
def grant_access(user_id: int, category_id: int, write_access: bool = False, admin_user: User = Depends(auth.get_current_admin_user)):
    return categories_services.grant_read_access(user_id, category_id, write_access, admin_user)


@router.get('/{category_id}/read-content', response_model=None)
def category_content(category_id: int, user: User = Depends(auth.get_current_user)):
    return categories_services.get_read_content(category_id, user)


@router.post('/{category_id}/grant-write-access', response_model=None)
def grant_write_access(user_id: int, category_id: int, admin_user: User = Depends(auth.get_current_admin_user)):
    return categories_services.grant_write_access(user_id, category_id, admin_user)


@router.post('/{category_id}/topics', response_model=None)
def create_topic(category_id: int, title: str, user: User = Depends(auth.get_current_user)):
    return categories_services.post_topic(category_id, title, user)


@router.get('/{category_id}/write-content', response_model=None)
def get_content(category_id: int, user: User = Depends(auth.get_current_user)):
    return categories_services.get_write_content(category_id, user)


@router.delete('/{category_id}/revoke-access', response_model=None)
def revoke_category_access(user_id: int, category_id: int, admin_user: User = Depends(auth.get_current_admin_user)):
    return categories_services.revoke_access(user_id, category_id, admin_user)


@router.get('/{category_id}/privileged_users', response_model=None)
def view_privileged_users(category_id: int, admin_user: User = Depends(auth.get_current_admin_user)):
    privileged_users = categories_services.get_privileged_users(category_id)

    if not privileged_users:
        raise NotFoundException(detail='No privileged users found')

    return {'category_id': category_id, 'privileged_users': privileged_users}    