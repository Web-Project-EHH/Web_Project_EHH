from fastapi import HTTPException
from fastapi.responses import JSONResponse
from data.database import read_query, insert_query, update_query
from data.models.category import Category, CategoryResponse
from typing import List
from common.responses import NoContent
from common.exceptions import ConflictException, NotFoundException


def get_categories(category_id: int = None, name: str = None, 
                   sort_by: str = None, sort: str = None) -> CategoryResponse | List[CategoryResponse] | HTTPException:

    query = '''SELECT category_id, name FROM categories'''
    params = []

    if category_id:
        query += ''' WHERE category_id = ?'''
        params.append(category_id)

    if name:
        query += ''' AND name LIKE ?''' if category_id else ''' WHERE name LIKE ?'''
        params.append(f'%{name}%')

    if sort_by:

        query += f''' ORDER BY {sort_by}'''

    if sort:
        
        query += f" {sort.upper()}"

    categories = read_query(query, tuple(params))
    
    if len(categories) < 2:
        return next((CategoryResponse.from_query_result(*row) for row in categories), None)
    
    else:
        return [CategoryResponse.from_query_result(*obj) for obj in categories]
    

def create(category: Category) -> Category | ConflictException:

    if exists(name=category.name):

        raise ConflictException('Category with that name already exists')
    
    generated_id = insert_query('''INSERT INTO categories (name, is_locked, is_private) VALUES (?, ?, ?)''',
                                 (category.name, category.is_locked, category.is_private))

    category.id = generated_id

    return category
    

def exists(category_id: int = None, name: str = None) -> bool:
    
    category = None

    if category_id:
        category = read_query('''SELECT category_id FROM categories WHERE category_id = ?
                            LIMIT 1''', (category_id,))
    
    elif name:
        category = read_query('''SELECT category_id FROM categories WHERE name = ?
                            LIMIT 1''', (name,))
    
    return bool(category)


def delete(category_id: int, delete_topics: bool = None) -> JSONResponse | NotFoundException:

    if not exists(category_id=category_id):

        raise NotFoundException(message='Category does not exist')
    
    category_name = name(category_id)
    
    update_query('''DELETE FROM users_categories_permissions WHERE category_id = ?''', (category_id,))

    topics = has_topics(category_id)
    
    if delete_topics and topics:

        update_query('''DELETE FROM replies
                        WHERE topic_id IN (SELECT t.topic_id 
                        FROM topics t 
                        WHERE t.category_id = ?)''', (category_id,))
        
        update_query('''DELETE FROM topics WHERE category_id = ?''', (category_id,))

    update_query('''DELETE FROM categories WHERE category_id = ?''', (category_id,))

    return JSONResponse(content={'message': f'Category {category_name} with ID:{category_id} has been deleted' +
                   (", along with its topics." if (delete_topics and topics) else ".")}, status_code=200)
    

def update(old_category: Category, new_category: Category) -> Category:

    if not exists(name=old_category.name):
        raise HTTPException(status_code=404, detail='Category not found')
    
    if exists(name=new_category.name):
        raise HTTPException(status_code=409, detail='Category with such name already exists')
    
    merged = Category(name=new_category.name or old_category.name,
                      is_locked=new_category.is_locked or old_category.is_locked,
                      is_private=new_category.is_private or old_category.is_private)
    
    update_query('''UPDATE categories SET name = ?, is_locked = ?, is_private = ? WHERE name = ?''',
                 (merged.name, merged.is_locked, merged.is_private, old_category.name))

    return merged


def has_topics(category_id: int) -> bool:

    topics = read_query('''SELECT topic_id FROM topics WHERE category_id = ? LIMIT 1''', (category_id,))

    return bool(topics)

def name(category_id: int) -> str:

    name = read_query('''SELECT name FROM categories WHERE category_id = ? LIMIT 1''', (category_id,))

    return name[0][0]

def get_id(name: str) -> int:

    id = read_query('''SELECT category_id FROM categories WHERE name = ? LIMIT 1''', (name,))

    return id[0][0]