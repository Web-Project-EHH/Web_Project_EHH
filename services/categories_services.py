from fastapi import HTTPException
from fastapi.responses import JSONResponse
from data.database import read_query, insert_query, update_query
from data.models.category import Category, CategoryResponse
from typing import List
from common.responses import NoContent
from common.exceptions import ConflictException, NotFoundException


def get_categories(category_id: int = None, name: str = None, 
                   sort_by: str = None, sort: str = None) -> CategoryResponse | List[CategoryResponse] | HTTPException:

    """
    Retrieve categories from the database based on optional filters.

    Args:
        category_id (int, optional): Filter by category ID
        name (str, optional): Filter categories by name (partial match)
        sort_by (str, optional): Column to sort by
        sort (str, optional): 'ASC' or 'DESC' for sorting order

    Returns:
        CategoryResponse | List[CategoryResponse]: Single or multiple category responses, or None if not found
        HTTPException: Raised on query execution failure
    """

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
    
    # Return single category if one is found, otherwise return a list
    if len(categories) < 2:
        return next((CategoryResponse.from_query_result(*row) for row in categories), None)
    
    else:
        return [CategoryResponse.from_query_result(*obj) for obj in categories]
    

def create(category: Category) -> Category | ConflictException:
    """
    Create a new category in the database.

    Args:
        category (Category): The category object to be created

    Returns:
        Category: The created category object with the assigned ID
        ConflictException: Raised if a category with the same name already exists
    """

    if exists(name=category.name):

        raise ConflictException('Category with that name already exists')
    
    generated_id = insert_query('''INSERT INTO categories (name, is_locked, is_private) VALUES (?, ?, ?)''',
                                 (category.name, category.is_locked, category.is_private))

    category.id = generated_id

    return category
    

def exists(category_id: int = None, name: str = None) -> bool:
    
    """
    Check if a category exists in the database by either category ID or name.

    Args:
        category_id (int, optional): The ID of the category to check
        name (str, optional): The name of the category to check

    Returns:
        bool: True if the category exists, False otherwise
    """
    
    category = None

    # If id is provided, query the database for that id
    if category_id:
        category = read_query('''SELECT category_id FROM categories WHERE category_id = ?
                            LIMIT 1''', (category_id,))
    
    # If name is provided, query the database for that name
    elif name:
        category = read_query('''SELECT category_id FROM categories WHERE name = ?
                            LIMIT 1''', (name,))
    
    return bool(category)


def delete(category_id: int, delete_topics: bool = False) -> JSONResponse | NotFoundException:

    """
    Delete a category from the database, optionally deleting associated topics and replies.

    Args:
        category_id (int): The ID of the category to be deleted.
        delete_topics (bool, optional): A flag indicating whether to delete associated topics
                                         and replies (default is False)

    Returns:
        JSONResponse: A response indicating the success of the deletion
        
    Raises:
        NotFoundException: If the category with the specified ID does not exist.
        (The delete router also raises an Integrity Error if a category with existing 
        topics is attempted to be deleted)
    """

    if not exists(category_id=category_id):

        raise NotFoundException(message='Category does not exist')
    
    category_name = name(category_id)
    
    update_query('''DELETE FROM users_categories_permissions WHERE category_id = ?''', (category_id,))

    topics = has_topics(category_id)
    
    if delete_topics and topics:

        # First delete the replies of the category's topics 
        update_query('''DELETE FROM replies
                        WHERE topic_id IN (SELECT t.topic_id 
                        FROM topics t 
                        WHERE t.category_id = ?)''', (category_id,))
        
        # Then delete the topics
        update_query('''DELETE FROM topics WHERE category_id = ?''', (category_id,))

    #Finally delete the category
    update_query('''DELETE FROM categories WHERE category_id = ?''', (category_id,))

    return JSONResponse(content={'message': f'Category {category_name} with ID:{category_id} has been deleted' +
                   (", along with its topics." if (delete_topics and topics) else ".")}, status_code=200)
    

def update(old_category: Category, new_category: Category) -> Category:

    """
    Update the details of an existing category in the database.

    Args:
        old_category (Category): The current category object that is to be updated
        new_category (Category): The new category object containing updated details

    Returns:
        Category: The updated category object

    Raises:
        HTTPException: 
            404 if the category to be updated is not found
            409 if a category with the new name already exists
    """

    if not exists(name=old_category.name):
        raise HTTPException(status_code=404, detail='Category not found')
    
    if exists(name=new_category.name):
        raise HTTPException(status_code=409, detail='Category with such name already exists')
    
    #Take the new parameters if given, otherwise keep the old ones
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