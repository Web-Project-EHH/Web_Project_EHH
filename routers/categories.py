from fastapi.responses import JSONResponse
from services import categories_services
from fastapi import APIRouter, HTTPException
from common.exceptions import ConflictException, ForbiddenException, NotFoundException
from data.models.category import Category, CategoryResponse
from typing import List
from fastapi import Query
from typing import Literal, Optional, Union
from mariadb import IntegrityError

router = APIRouter(prefix='/categories')

@router.get('/', response_model=None)
def get_categories(category_id: Optional[int] = Query(default=None), 
                   name: Optional[str] = Query(default=None), 
                   sort_by: Literal["name", "category_id"] | None = Query(default=None), 
                   sort: Literal["asc", "desc",] | None = Query(default=None)) -> List[CategoryResponse] | CategoryResponse | HTTPException:

    categories = categories_services.get_categories(category_id=category_id,name=name,sort_by=sort_by,sort=sort)

    if not categories:
        raise HTTPException(status_code=404, detail='No matching categories found')
    
    return categories


@router.post('/', response_model=None)
def create_category(category: Category) -> JSONResponse | HTTPException:
    try:

        new_category = categories_services.create(category)

        return JSONResponse(content={'message': f'Category {new_category.name} with ID: {new_category.id} has been created'},
                                status_code=201)

    except ConflictException as e:
        
        raise HTTPException(status_code=409, detail=e.message)


@router.put('/', response_model=None)
def update_category(old_category: Category, new_category: Category) -> JSONResponse | HTTPException:
    old_category_id = categories_services.get_id(old_category.name)

    updated = categories_services.update(old_category, new_category)

    if not updated:
        raise HTTPException(status_code=400, detail='Category could not be updated')

    return JSONResponse(content={'message': f'Category with ID: {old_category_id} has been updated'},
                        status_code=200)


@router.delete('/', response_model=None)
def delete_category(category_id: int, delete_topics: bool = None) -> JSONResponse | HTTPException:

    try:
        response = categories_services.delete(category_id, delete_topics)
        return response

    except NotFoundException as nf:

        raise HTTPException(status_code=404, detail=nf.message)
    
    except IntegrityError as i:

        raise HTTPException(status_code=403, detail='Cannot delete a category that includes topics.')



