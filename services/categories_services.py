from data.database import read_query, insert_query, update_query
from data.models.category import Category, CategoryChangeName, CategoryChangeNameID, CategoryCreate, CategoryResponse
from typing import List
from common.exceptions import ConflictException, ForbiddenException, NotFoundException, BadRequestException
from data.models.topic import TopicCategoryResponseAdmin, TopicCategoryResponseUser
from data.models.user import User


def get_categories(current_user: User, 
                   category_id: int = None, name: str = None, 
                   sort_by: str = None, sort: str = None,
                   limit: int = 10, offset: int = 0,) -> CategoryResponse | List[CategoryResponse] | None:
    
    """
    Retrieve categories from the database with optional filtering, sorting, and pagination.

    Args:
        category_id (int, optional): Filter by category ID. Defaults to None.
        name (str, optional): Filter by category name using a partial match. Defaults to None.
        sort_by (str, optional): Column name to sort the results by. Defaults to None.
        sort (str, optional): Sort order ('ASC' or 'DESC'). Defaults to None.
        limit (int, optional): Maximum number of results to return. Defaults to 10.
        offset (int, optional): Number of rows to skip before starting to return rows. Defaults to 0.

    Returns:
        CategoryResponse | List[CategoryResponse] | None: A single CategoryResponse if one result is found,
        a list of CategoryResponse objects if multiple results are found, or None if no results are found.
    """
   
    query = '''SELECT category_id, name FROM categories WHERE 1=1'''
    params = []

    if category_id:
        query += ''' AND category_id = ?'''
        params.append(category_id)

    if not current_user.is_admin:
        query += ''' AND is_private = ?''' 
        params.append(0)

    if name:
        query += ''' AND name LIKE ?'''
        params.append(f'%{name}%')

    if sort_by:
        query += f''' ORDER BY {sort_by}'''

    if sort:
        query += f" {sort.upper()}"

    query += ''' LIMIT ? OFFSET ?'''
    params.extend([limit, offset])

    categories = read_query(query, tuple(params))


    if len(categories) > 1: # Return a list of objects if more than one instance is found
        return [CategoryResponse.from_query_result(*obj) for obj in categories]
    
    else: # Otherwise return a single object
        return next((CategoryResponse.from_query_result(*row) for row in categories), None)
    

def create(category: CategoryCreate) -> Category | None:

    """
    Create a new category in the database.
    
    Args:
        category (Category): The category object to be created. Must contain the name, is_locked, and is_private attributes.
    
    Returns:
        Category | None: The created category object with the generated ID, or None if the category could not be created.
    
    Raises:
        ConflictException: If a category with the same name already exists.
    """

    if exists(name=category.name):
        raise ConflictException(detail='Category with that name already exists')
    
    generated_id = insert_query('''INSERT INTO categories (name, is_locked, is_private) VALUES (?, ?, ?)''',
                                 (category.name, category.is_locked, category.is_private))

    return Category(id=generated_id, name=category.name, is_locked=category.is_locked, is_private=category.is_private) if generated_id else None
    

def exists(category_id: int = None, name: str = None) -> bool:
    
    category = None

    if category_id: # If an id is provided, check the database for the id
        category = read_query('''SELECT category_id FROM categories WHERE category_id = ?
                            LIMIT 1''', (category_id,))
    
    elif name: # Or if a name is provided, check the database for the name
        category = read_query('''SELECT category_id FROM categories WHERE name = ?
                            LIMIT 1''', (name,))
    
    return bool(category)


def delete(category_id: int, delete_topics: bool = False) ->  str | None:
    
    """
    Delete a category and optionally its associated topics and replies.
    
    Args:
        category_id (int): The ID of the category to be deleted.
        delete_topics (bool, optional): If True, deletes topics and replies associated with the category. Defaults to False.
    
    Returns:
        str | None: A message indicating what was deleted, or None if the category was not deleted.
    
    Raises:
        NotFoundException: If the category does not exist.
    """

    if not exists(category_id=category_id):
        raise NotFoundException(detail='Category does not exist')
    
    # Fist delete the category from users_categories_permission table
    update_query('''DELETE FROM users_categories_permissions WHERE category_id = ?''', (category_id,))

    topics = has_topics(category_id)

    delete_from_replies = None
    delete_from_topics = None
    
    if delete_topics and topics: # If delete topics was selected, check if any exist and then delete them

        delete_from_replies = update_query('''DELETE FROM replies
                        WHERE topic_id IN (SELECT t.topic_id 
                        FROM topics t 
                        WHERE t.category_id = ?)''', (category_id,))
        
        delete_from_topics = update_query('''DELETE FROM topics WHERE category_id = ?''', (category_id,))

    # Finally delete the category itself
    deleted = update_query('''DELETE FROM categories WHERE category_id = ?''', (category_id,))

    if not deleted:
        return None
    
    else:

        if delete_from_replies and delete_from_topics:
            return 'everything deleted' 
    
        return 'only category deleted'
    

def update_name(old_category: CategoryChangeNameID, new_category: CategoryChangeName) -> CategoryResponse | None:

    """
    Update the name of an existing category.
    
    Args:
        old_category (CategoryResponse): The current category details, including its name or ID.
        new_category (CategoryResponse): The new category details, including the new name.
    
    Returns:
        CategoryResponse | None: The updated category details if the update was successful, otherwise None.
    
    Raises:
        NotFoundException: If the old category does not exist.
        ConflictException: If a category with the new name already exists.
        BadRequestException: If the new category name is not provided.
    """

    if not exists(category_id=old_category.id):
        raise NotFoundException(detail='Category not found')
    
    if exists(name=new_category.name):
        raise ConflictException(detail='Category with such name already exists')
    
    if not new_category.name:
        raise BadRequestException(detail='New name has to be given')

    query = '''UPDATE categories SET name = ?'''
    params = [new_category.name]

    if old_category.id: # Check by id if provided

        query +=  ''' WHERE category_id = ?'''
        params.append(old_category.id)
    
    elif old_category.name: # Otherwise check by name

        query += ''' WHERE name = ?'''
        params.append(old_category.name)

    updated = update_query(query, tuple(params))

    merged = CategoryResponse(id=get_id(new_category.name), name=new_category.name or old_category.name)

    return merged if (merged and updated) else None


def has_topics(category_id: int) -> bool:

    topics = read_query('''SELECT topic_id FROM topics WHERE category_id = ? LIMIT 1''', (category_id,))

    return bool(topics)


def get_name(category_id: int) -> str:

    name = read_query('''SELECT name FROM categories WHERE category_id = ? LIMIT 1''', (category_id,))

    return name[0][0]


def get_id(name: str) -> int:

    id = read_query('''SELECT category_id FROM categories WHERE name = ? LIMIT 1''', (name,))

    return id[0][0]


def lock_unlock(category_id: int) -> str | None:

    """
    Lock or unlock a category based on its current state.
    
    Args:
        category_id (int): The ID of the category to lock or unlock.
    
    Returns:
        str | None: A string indicating the result of the operation:
            - 'unlocked' if the category was successfully unlocked.
            - 'unlock failed' if the unlock operation failed.
            - 'locked' if the category was successfully locked.
            - 'lock failed' if the lock operation failed.
            - None if the category does not exist.
    Raises:
        NotFoundException: If the category with the given ID does not exist.
    """

    if not exists(category_id):
        raise NotFoundException(detail='Category not found')

    if is_locked(category_id): # If the category is already locked, unlock it

        unlock_category = update_query('''UPDATE categories SET is_locked = ? WHERE category_id = ?''', (False, category_id))

        if not unlock_category:
            return 'unlock failed'

        return 'unlocked'

    else: # Otherwise, lock it
        lock_category = update_query('''UPDATE categories SET is_locked = ? WHERE category_id = ?''', (True, category_id))

        if not lock_category:
            return 'lock failed'
        
        return 'locked'


def is_locked(category_id: int) -> bool:

    locked_row = read_query('''SELECT is_locked FROM categories WHERE category_id = ?''', (category_id,))

    locked_bool = locked_row[0][0]

    return locked_bool


def is_private(category_id: int) -> bool:

    private_row = read_query('''SELECT is_private FROM categories WHERE category_id = ?''', (category_id,))

    private_bool = private_row[0][0]

    return private_bool


def privatise_unprivatise(category_id: int) -> str | None:

    """
    Toggles the privacy status of a category based on its current state.

    Args:
        category_id (int): The ID of the category to be toggled.
    
    Returns:
        str | None: A message indicating the result of the operation, or None if the category does not exist.
    
    Raises:
        NotFoundException: If the category with the given ID does not exist.
    """

    if not exists(category_id):
        raise NotFoundException(detail='Category not found')

    if is_private(category_id): # If the category is already private, make it public
            
            make_public = update_query('''UPDATE categories SET is_private = ? WHERE category_id = ?''', (False, category_id))
    
            if not make_public:
                return 'made public failed'
    
            return 'made public'
    
    else: # Otherwise, make it private
    
        make_private = update_query('''UPDATE categories SET is_private = ? WHERE category_id = ?''', (True, category_id))
    
        if not make_private:
            return 'made private failed'
        
        return 'made private'
    

def get_by_id(category_id: int, current_user: User):

    if not exists(category_id):
        return None
    
    if current_user.is_admin:
        
        category = read_query('''SELECT category_id, name, is_locked, is_private FROM categories
                          WHERE category_id = ?''', (category_id,))
    
        topics = read_query('''SELECT topic_id, title, user_id, is_locked, COALESCE(best_reply_id, NULL) AS best_reply_id, category_id FROM topics
                        WHERE category_id = ?''', (category_id,))
        
        return {'Category': Category.from_query_result(*category[0] if category else 'No categories'), 
            'Topics': [TopicCategoryResponseAdmin.from_query(*obj) for obj in topics] if topics else 'No topics'}
        
    else:
        category = read_query('''SELECT category_id, name FROM categories
                          WHERE is_private = 0 AND category_id = ?''', (category_id,))
        
        if category:
        
            topics = read_query('''SELECT topic_id, title, user_id, COALESCE(best_reply_id, NULL) AS best_reply_id, category_id FROM topics
                        WHERE is_locked = 0 AND category_id = ?''', (category_id,))
    
            return {'Category': CategoryResponse.from_query_result(*category[0]) if category else 'No categories', 
                    'Topics': [TopicCategoryResponseUser.from_query(*obj) for obj in topics] if topics else 'No topics'}
        

def grant_read_access(user_id: int, category_id: int, write_access: bool, admin_user: User) -> bool:
    if not admin_user.is_admin:
        raise ForbiddenException(detail='You do not have permission to access this resource')
    
    category_status = read_query("SELECT * FROM categories WHERE category_id = ? AND is_private = 1", (category_id,))
    if not category_status:
        raise NotFoundException(detail='Category not found or not private')
    
    existing_access = read_query("SELECT * FROM users_categories_permissions WHERE user_id = ? AND category_id = ?", (user_id, category_id))
    if existing_access:
        update_query("UPDATE users_categories_permissions SET write_access = ? WHERE user_id = ? AND category_id = ?", (write_access, user_id, category_id))
        return {'message': 'Access updated'}
    else:
        insert_query("INSERT INTO users_categories_permissions (user_id, category_id, write_access) VALUES (?, ?, ?)", (user_id, category_id, write_access))
        return {'message': 'Access granted'}
    

def has_read_access(user_id: int, category_id: int) -> bool:
    user_access = read_query("SELECT * FROM users_categories_permissions WHERE user_id = ? AND category_id = ?", (user_id, category_id))
    return bool(user_access)


def get_read_content(category_id: int, user: User) -> dict:
    category_data = read_query("SELECT * FROM categories WHERE category_id = ?", (category_id,))
    if not category_data:
        raise NotFoundException(detail='Category not found')
    is_private = category_data[0][3]
    if is_private and not has_read_access(user.id, category_id):
        raise ForbiddenException(detail='You do not have permission to access this resource')
    
    topics = read_query("SELECT * FROM topics WHERE category_id = ?", (category_id,))
    replies = read_query("SELECT * FROM replies WHERE topic_id IN (SELECT topic_id FROM topics WHERE category_id = ?)", (category_id,))
    return {'topics': topics, 'replies': replies}


def grant_write_access(user_id: int, category_id: int, admin_user: User) -> bool:
    if not admin_user.is_admin:
        raise ForbiddenException(detail='You do not have permission to access this resource')
    
    category_data = read_query("SELECT * FROM categories WHERE category_id = ?", (category_id,))
    if not category_data:
        raise NotFoundException(detail='Category not found or is not private')
    existing_access = read_query("SELECT * FROM users_categories_permissions WHERE user_id = ? AND category_id = ?", (user_id, category_id)) 
    if existing_access:
        update_query("UPDATE users_categories_permissions SET write_access = ? WHERE user_id = ? AND category_id = ?", (True, user_id, category_id))
        return {'message': 'Write access updated'}
    
    else:
        insert_query("INSERT INTO users_categories_permissions (user_id, category_id, write_access) VALUES (?, ?, ?)", (user_id, category_id, True))
        return {'message': 'Write access granted'}
    

def has_write_access(user_id: int, category_id: int) -> bool:
    user_access = read_query("SELECT * FROM users_categories_permissions WHERE user_id = ? AND category_id = ?", (user_id, category_id))
    return bool(user_access)    


def post_topic(category_id: int, title: str, user: User) -> int:
    if not has_read_access(user.id, category_id):
        raise ForbiddenException(detail='You do not have permission to access this resource')
    
    topic_id = insert_query("INSERT INTO topics (category_id, title, user_id) VALUES (?, ?, ?)", (category_id, title, user.id))
    return topic_id


def get_write_content(category_id: int, user: User) -> dict:
    if not has_write_access(user.id, category_id):
        raise ForbiddenException(detail='You do not have permission to access this resource')
    
    category_data = read_query("SELECT * FROM categories WHERE category_id = ?", (category_id,))
    if not category_data:
        raise NotFoundException(detail='Category not found or is not private')
    
    is_private = category_data[0][3]
    if is_private and not has_read_access(user.id, category_id):
        raise ForbiddenException(detail='You do not have permission to access this resource')
    topics = read_query("SELECT * FROM topics WHERE category_id = ?", (category_id,))
    replies = read_query("SELECT * FROM replies WHERE topic_id IN (SELECT topic_id FROM topics WHERE category_id = ?)", (category_id,))
    return {'topics': topics, 'replies': replies}


def revoke_access(user_id: int, category_id: int, admin_user: User) -> bool:
    if not admin_user.is_admin:
        raise ForbiddenException(detail='You do not have permission to access this resource')
    
    access_data = read_query("SELECT * FROM users_categories_permissions WHERE user_id = ? AND category_id = ?", (user_id, category_id))
    if not access_data:
        raise NotFoundException(detail='User does not have access to this category')
    
    update_query("DELETE FROM users_categories_permissions WHERE user_id = ? AND category_id = ?", (user_id, category_id))
    return {'message': 'Access revoked'}


def get_privileged_users(category_id: int) -> List[User]:
    privileged_users = read_query('SELECT u.user_id, u.username, u.email, u.first_name, u.last_name, p.write_access FROM users u JOIN users_categories_permissions p ON u.user_id = p.user_id WHERE p.category_id = ?', (category_id,))
    return [
        {
            'user_id': user[0], 
            'username': user[1], 
            'email': user[2], 
            'first_name': user[3], 
            'last_name': user[4], 
            'write_access': bool(user[5])
            } 
            for user in privileged_users
    ]

def count_categories() -> int:
    count = read_query('SELECT COUNT(*) FROM categories')
    return count[0][0] if count else 0