from datetime import datetime
from fastapi import HTTPException
from data.database import read_query, insert_query, update_query
from data.models.reply import Reply, ReplyResponse
from typing import List
from common.exceptions import ConflictException, NotFoundException, ForbiddenException, BadRequestException
from services import users_services

def get_replies(reply_id: int = None, text: str = None, user_id: int = None, user_name: str = None,
                topic_id: int = None, topic_title: str = None, sort_by: str = None, sort: str = None,
                start_date: datetime = None, end_date: datetime = None, limit: int = 10,
                offset: int = 0) -> List[Reply] | Reply:
    
    """
    Retrieve replies from the database based on various filtering and sorting criteria.

    Args:
        reply_id (int, optional): The ID of the reply to filter by.
        text (str, optional): Text to search for within replies.
        user_id (int, optional): The ID of the user who made the replies.
        user_name (str, optional): The username of the user who made the replies.
        topic_id (int, optional): The ID of the topic related to the replies.
        topic_title (str, optional): The title of the topic related to the replies.
        sort_by (str, optional): Column name to sort the results by.
        sort (str, optional): The sort order; should be either 'ASC' or 'DESC'.
        start_date (datetime, optional): Filter replies created after this date.
        end_date (datetime, optional): Filter replies created before this date.
        limit (int, optional): The maximum number of replies to return (default is 10).
        offset (int, optional): The number of replies to skip before starting to collect the result set (default is 0).

    Returns:
        List[Reply] | Reply: A list of Reply objects if multiple replies match the criteria, 
                             or a single Reply object if only one matches, or None if no replies are found.
    """

    query = '''SELECT reply_id, text, user_id, topic_id, created, edited FROM replies WHERE 1=1'''
    params = []

    if reply_id:
        query += ''' AND reply_id = ?'''
        params.append(reply_id)

    if text:
        query += ''' AND text LIKE ?'''
        params.append(f'%{text}%')

    if user_id or user_name:
        user_id_row = read_query('''SELECT u.user_id FROM users u JOIN replies r ON u.user_id = r.user_id WHERE u.username = ? LIMIT 1''', (user_name,)) if user_name else None
        user_id = user_id_row[0][0] if user_id_row else user_id
        query += ''' AND user_id = ?'''
        params.append(user_id)

    if topic_id or topic_title:
        topic_id_row = read_query('''SELECT t.topic_id FROM topics t 
                                  JOIN replies r ON t.topic_id = r.topic_id 
                                  WHERE t.title = ? LIMIT 1''', (topic_title,)) if topic_title else None
        topic_id = topic_id_row[0][0] if topic_id_row else topic_id
        query += ''' AND topic_id = ?'''
        params.append(topic_id)

    if start_date:
        query += ''' AND created > ?'''
        params.append(start_date)

    if end_date:
        query += ''' AND created < ?'''
        params.append(end_date)

    if sort_by:
        query += f''' ORDER BY {sort_by}'''

        if sort:
            query += f''' {sort.upper()}'''

    query += ''' LIMIT ? OFFSET ?'''
    params.extend([limit, offset])

    replies = read_query(query, tuple(params))

    # Return a list of objects if more than one is found, otherwise return a single object
    if len(replies) > 1:
        return [Reply.from_query_result(*obj) for obj in replies]

    else:
        return next((Reply.from_query_result(*row) for row in replies), None)
    

def create(reply: Reply) -> Reply | HTTPException | None:

    """
    Creates a new reply in the database.
    
    Args:
        reply (Reply): The reply object containing the details of the reply to be created.
    
    Returns:
        Reply: The created reply object with the generated ID.
        HTTPException: If the topic does not exist or if the same reply is posted more than twice.
        None: If the reply could not be created.
    
    Raises:
        NotFoundException: If the topic does not exist.
        ForbiddenException: If the same reply is posted more than twice.
    """

    topic = read_query('''SELECT topic_id FROM topics WHERE topic_id = ?''', (reply.topic_id,))

    if not topic:
        raise NotFoundException(detail='Topic does not exist')
    
    generated_id = insert_query('''INSERT INTO replies (text, user_id, topic_id, created, edited) VALUES (?, ?, ?, ?, ?)''',
                                (reply.text, reply.user_id, reply.topic_id, reply.created, reply.edited))
    
    reply.id = generated_id

    return reply if reply else None


def edit_text(old_reply: ReplyResponse, new_reply: ReplyResponse) -> ReplyResponse | HTTPException | None:

    """
    Update an existing reply with new information.
    
    Args:
        old_reply (Reply): The original reply object to be updated.
        new_reply (Reply): The new reply object containing updated information.
    
    Returns:
        Reply: The updated reply object if the update is successful.
        HTTPException: If the original reply does not exist.
        None: If the update fails for any other reason.
    
    Raises:
        NotFoundException: If the original reply does not exist in the database.
    """
    
    if not exists(old_reply.id):
        raise NotFoundException(detail='Reply does not exist')
    
    if new_reply.text == '':
    
        new_reply.text = fetch_text(old_reply.id)

    merged = ReplyResponse(id=old_reply.id, text = new_reply.text or old_reply.text)

    edited = update_query('''UPDATE replies SET text = ?, edited = ?
                       WHERE reply_id = ?''', (merged.text, True, old_reply.id))
    
    return merged if (merged and edited) else None


def exists(reply_id: int) -> bool:

    """
    Check if a reply with the given reply_id exists in the database.
    
    Args:
        reply_id (int): The ID of the reply to check.
    
    Returns:
        bool: True if the reply exists, False otherwise.
    """
     
    reply = read_query('''SELECT reply_id FROM replies WHERE reply_id = ? LIMIT 1''', (reply_id,))
    
    return bool(reply)


def delete(reply_id: int) -> str | HTTPException:

    """
    Deletes a reply from the database based on the given reply_id.
    
    Args:
        reply_id (int): The ID of the reply to be deleted.
    
    Returns:
        str: A confirmation message indicating the reply was deleted.
        HTTPException: An exception if the reply does not exist.
    
    Raises:
        NotFoundException: If the reply with the given ID does not exist.
    """

    if not exists(reply_id):
        raise NotFoundException(detail='Reply not found')
    
    deleted = update_query('''DELETE FROM replies WHERE reply_id = ?''', (reply_id,))
    
    return 'reply deleted'


def fetch_text(reply_id: int) -> str:

    reply_text_row = read_query('''SELECT text FROM replies WHERE reply_id = ?''', (reply_id,))

    return str(reply_text_row[0][0])