from fastapi import HTTPException
from data.database import read_query, insert_query, update_query
from data.models.category import Category, CategoryResponse
from typing import List
from common.exceptions import ConflictException, NotFoundException, BadRequestException


def get_categories(category_id: int = None, name: str = None, 
                   sort_by: str = None, sort: str = None,
                   limit: int = 10, offset: int = 0) -> CategoryResponse | List[CategoryResponse] | None:

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

    query += ''' LIMIT ? OFFSET ?'''
    params.extend([limit, offset])

    categories = read_query(query, tuple(params))


    # Return a list of objects if more than one are found, otherwise return a single object
    if len(categories) > 1:
        return [CategoryResponse.from_query_result(*obj) for obj in categories]
    
    else:
        return next((CategoryResponse.from_query_result(*row) for row in categories), None)
    

def create(category: Category) -> Category | HTTPException | None:
    
    """
    Create a new category in the database.

    Args:
        category (Category): The category object to be created

    Returns:
        Category: The created category object with the assigned ID
        ConflictException: Raised if a category with the same name already exists
    """

    if exists(name=category.name):
        raise ConflictException(detail='Category with that name already exists')
    
    generated_id = insert_query('''INSERT INTO categories (name, is_locked, is_private) VALUES (?, ?, ?)''',
                                 (category.name, category.is_locked, category.is_private))

    category.id = generated_id

    return category if category else None
    

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


def delete(category_id: int, delete_topics: bool = False) ->  str | None:
    
    """
    Deletes a category and optionally its associated topics and replies.
    
    Args:
        category_id (int): The ID of the category to be deleted.
        delete_topics (bool, optional): If True, deletes the topics and their replies associated with the category. Defaults to False.
    
    Returns:
        str: A message indicating what was deleted.
        None: If the category could not be deleted.
    
    Raises:
        NotFoundException: If the category does not exist.
    """

    if not exists(category_id=category_id):
        raise NotFoundException(detail='Category does not exist')
    
    update_query('''DELETE FROM users_categories_permissions WHERE category_id = ?''', (category_id,))

    topics = has_topics(category_id)

    delete_from_replies = None
    delete_from_topics = None
    
    if delete_topics == True and topics == True:

        # First delete the replies of the category's topics 
        delete_from_replies = update_query('''DELETE FROM replies
                        WHERE topic_id IN (SELECT t.topic_id 
                        FROM topics t 
                        WHERE t.category_id = ?)''', (category_id,))
        
        # Then delete the topics
        delete_from_topics = update_query('''DELETE FROM topics WHERE category_id = ?''', (category_id,))

    #Finally delete the category
    deleted = update_query('''DELETE FROM categories WHERE category_id = ?''', (category_id,))

    if not deleted:
        return None
    
    elif deleted:

        if delete_from_replies and delete_from_topics:
            return 'everything deleted' 
    
    return 'only category deleted'
    

def update_name(old_category: CategoryResponse, new_category: CategoryResponse) -> CategoryResponse | HTTPException | None:

    """
    Update the name of an existing category.
   
    Args:
        old_category (CategoryResponse): The current category details, including its name and ID.
        new_category (CategoryResponse): The new category details, including the new name.
    
    Returns:
        CategoryResponse: The updated category details if the update is successful.
        None: If the update operation fails.
    
    Raises:
        NotFoundException: If the old category does not exist.
        ConflictException: If a category with the new name already exists.
        BadRequestException: If the new name is not provided.
    """


    if not (exists(name=old_category.name) or exists(category_id=old_category.id)):
        raise NotFoundException(detail='Category not found')
    
    if exists(name=new_category.name):
        raise ConflictException(detail='Category with such name already exists')
    
    if not new_category.name:
        raise BadRequestException(detail='New name has to be given')

    query = '''UPDATE categories SET name = ?'''
    params = [new_category.name]

    if old_category.id:
    
        query +=  ''' WHERE category_id = ?'''
        params.append(old_category.id)
    
    elif old_category.name:

        query += ''' WHERE name = ?'''
        params.append(old_category.name)

    updated = update_query(query, tuple(params))

    merged = CategoryResponse(id=get_id(new_category.name), name=new_category.name or old_category.name)

    return merged if (merged and updated) else None


def has_topics(category_id: int) -> bool:

    """
    Checks if a category has any associated topics.

    Args:
        category_id (int): The ID of the category to check.

    Returns:
        bool: True if the category has at least one topic, False otherwise.
    """

    topics = read_query('''SELECT topic_id FROM topics WHERE category_id = ? LIMIT 1''', (category_id,))

    return bool(topics)


def name(category_id: int) -> str:

    """
    Retrieves the name of a category from the database based on the given category ID.

    Args:
        category_id (int): The ID of the category whose name is to be retrieved.

    Returns:
        str: The name of the category.

    Raises:
        IndexError: If no category with the given ID is found.
    """

    name = read_query('''SELECT name FROM categories WHERE category_id = ? LIMIT 1''', (category_id,))

    return name[0][0]


def get_id(name: str) -> int:
    """
    Retrieve the ID of a category based on its name.

    Args:
        name (str): The name of the category.

    Returns:
        int: The ID of the category.

    Raises:
        IndexError: If no category with the given name is found.
    """

    id = read_query('''SELECT category_id FROM categories WHERE name = ? LIMIT 1''', (name,))

    return id[0][0]


def lock_unlock(category_id: int) -> str | HTTPException | None:

    """
    Locks or unlocks a category based on its current state.

    Args:
        category_id (int): The ID of the category to be locked or unlocked.
    
    Returns:
        str: A message indicating the result of the operation ('locked', 'unlocked', 'lock failed', 'unlock failed').
        HTTPException: If the category is not found.
        None: If the operation does not return any specific result.
    
    Raises:
        NotFoundException: If the category with the given ID does not exist.
    """

    if not exists(category_id):
        raise NotFoundException(detail='Category not found')

    if is_locked(category_id):

        unlock_category = update_query('''UPDATE categories SET is_locked = ? WHERE category_id = ?''', (False, category_id))

        if not unlock_category:
            return 'unlock failed'

        return 'unlocked'

    else:
        lock_category = update_query('''UPDATE categories SET is_locked = ? WHERE category_id = ?''', (True, category_id))

        if not lock_category:
            return 'lock failed'
        
        return 'locked'


def is_locked(category_id: int) -> bool:

    """
    Checks if a category is locked based on its category ID.
    
    Args:
        category_id (int): The ID of the category to check.
    
    Returns:
        bool: True if the category is locked, False otherwise.
    """

    locked_row = read_query('''SELECT is_locked FROM categories WHERE category_id = ?''', (category_id,))

    locked_bool = locked_row[0][0]

    return locked_bool


def is_private(category_id: int) -> bool:

    """
    Checks if a category is marked as private.
    
    Args:
        category_id (int): The ID of the category to check.
    
    Returns:
        bool: True if the category is private, False otherwise.
    """

    private_row = read_query('''SELECT is_private FROM categories WHERE category_id = ?''', (category_id,))

    private_bool = private_row[0][0]

    return private_bool


def privatise_unprivatise(category_id: int) -> str | HTTPException | None:

    """
    Toggles the privacy status of a category based on its current state.
    If the category is currently private, it will be made public.
    If the category is currently public, it will be made private.

    Args:
        category_id (int): The ID of the category to be toggled.

    Returns:
        str: A message indicating the result of the operation.
        HTTPException: If the category is not found.
        None: If the operation is successful but no specific message is returned.

    Raises:
        NotFoundException: If the category with the given ID does not exist.
    """

    if not exists(category_id):
        raise NotFoundException(detail='Category not found')

    if is_private(category_id):
            
            make_public = update_query('''UPDATE categories SET is_private = ? WHERE category_id = ?''', (False, category_id))
    
            if not make_public:
                return 'made public failed'
    
            return 'made public'
    
    else:
    
        make_private = update_query('''UPDATE categories SET is_private = ? WHERE category_id = ?''', (True, category_id))
    
        if not make_private:
            return 'made private failed'
        
        return 'made private'