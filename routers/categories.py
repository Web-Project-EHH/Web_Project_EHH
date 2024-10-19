from fastapi.responses import JSONResponse
from pydantic import ValidationError
from services import categories_services
from fastapi import APIRouter, HTTPException
from common.exceptions import ConflictException, NotFoundException, BadRequestException, ForbiddenException
from data.models.category import Category, CategoryResponse
from typing import List
from fastapi import Query
from typing import Literal, Optional
from mariadb import IntegrityError


router = APIRouter(prefix='/categories')


@router.get('/', response_model=None)
def get_categories(category_id: Optional[int] = Query(default=None), 
                   name: Optional[str] = Query(default=None), 
                   sort_by: Literal["name", "category_id"] | None = Query(default=None), 
                   sort: Literal["asc", "desc",] | None = Query(default=None),
                   limit: int = Query(default=10, ge=1),
                   offset: int = Query(default=0, ge=0)) -> List[CategoryResponse] | CategoryResponse | HTTPException:

    categories = categories_services.get_categories(category_id=category_id,name=name,sort_by=sort_by,sort=sort,
                                                        limit=limit, offset=offset)
    
    if not categories:
        raise NotFoundException(detail="No matching categories found")

    return categories


@router.post('/', response_model=None)
def create_category(category: Category) -> Category | HTTPException:

        new_category = categories_services.create(category)

        if not new_category:
            raise BadRequestException(detail="Category could not be created")

        return new_category


@router.put('/', response_model=None)
def update_category(old_category: Category, new_category: Category) -> Category | HTTPException:
    
    updated = categories_services.update(old_category, new_category)

    if not updated:
        raise BadRequestException(detail='Category  could not be updated')

    return updated


@router.delete('/', response_model=None)
def delete_category(category_id: int = Query(int), delete_topics: bool = Query(False)) -> JSONResponse | HTTPException:

    try:

        response = categories_services.delete(category_id, delete_topics)
        
        if not response:
            raise BadRequestException(detail='Category could not be deleted')

        return response
    
    except IntegrityError:
        
        raise ForbiddenException(detail='Cannot delete a category that includes topics.')



