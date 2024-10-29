from datetime import datetime

from fastapi import Depends
from data.database import read_query, insert_query, update_query
from data.models.reply import Reply, ReplyCreate, ReplyResponse
from typing import List
from common.exceptions import ForbiddenException, NotFoundException
from data.models.user import User
from services import users_services

def get_replies(reply_id: int = None, text: str = None, user_id: int = None, user_name: str = None,
                topic_id: int = None, topic_title: str = None, sort_by: str = None, sort: str = None,
                start_date: datetime = None, end_date: datetime = None, limit: int = 10,
                offset: int = 0) -> List[Reply] | Reply | None:
    
    """
    Retrieve replies from the database based on various filters and sorting options.

    Args:
        reply_id (int, optional): Filter by reply ID.
        text (str, optional): Filter by text content, supporting partial matches.
        user_id (int, optional): Filter by user ID.
        user_name (str, optional): Filter by username.
        topic_id (int, optional): Filter by topic ID.
        topic_title (str, optional): Filter by topic title.
        sort_by (str, optional): Column name to sort the results by.
        sort (str, optional): Sort order, either 'ASC' or 'DESC'.
        start_date (datetime, optional): Filter replies created after this date.
        end_date (datetime, optional): Filter replies created before this date.
        limit (int, optional): Limit the number of replies returned. Defaults to 10.
        offset (int, optional): Offset for pagination. Defaults to 0.

    Returns:
        List[Reply] | Reply | None: A list of Reply objects if multiple replies are found,
                                    a single Reply object if only one reply is found,
                                    or None if no replies match the criteria.
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

    if len(replies) > 1: # If more than one instances are found, return a list of objects
        return [Reply.from_query_result(*obj) for obj in replies]

    else: # Otherwise return a single object
        return next((Reply.from_query_result(*row) for row in replies), None)
    

def create(reply: ReplyCreate, current_user: User) -> Reply | None:

    """
    Create a new reply in the database.

    Args:
        reply (Reply): The reply object containing the details of the reply to be created.
    
    Returns:
        Reply | None: The created reply with its generated ID if the insertion is successful, 
                      otherwise None.
    
    Raises:
        NotFoundException: If the topic associated with the reply does not exist.
    """

    topic = read_query('''SELECT topic_id FROM topics WHERE topic_id = ?''', (reply.topic_id,))

    if not topic:
        raise NotFoundException(detail='Topic does not exist')
    
    user_id = current_user.id
    
    generated_id = insert_query('''INSERT INTO replies (text, user_id, topic_id) VALUES (?, ?, ?)''',
                                (reply.text, user_id, reply.topic_id))

    return Reply(id=generated_id, text=reply.text, user_id=user_id, topic_id=reply.topic_id) if generated_id else None


def edit_text(old_reply: ReplyResponse, new_reply: ReplyResponse, current_user: User) -> ReplyResponse | None:

    """
    Edit the text of an existing reply.
    
    Args:
        old_reply (ReplyResponse): The original reply to be edited.
        new_reply (ReplyResponse): The new reply containing the updated text.

    Returns:
        ReplyResponse | None: The merged reply if the update is successful, otherwise None.
    
    Raises:
        NotFoundException: If the old reply does not exist.
    """

    if not exists(old_reply.id):
        raise NotFoundException(detail='Reply does not exist')
    
    reply_username = read_query('''SELECT u.username from users u
                                JOIN replies r on r.user_id = u.user_id
                                WHERE r.reply_id = ?''', (old_reply.id,))

    if current_user.username != reply_username[0][0]:
        raise ForbiddenException(detail='You are not allowed to edit this reply')
    
    if new_reply.text == '': # If the new text is an empty string, revert to the previous text
    
        new_reply.text = fetch_text(old_reply.id)

    merged = ReplyResponse(id=old_reply.id, text = new_reply.text or old_reply.text)

    edited = update_query('''UPDATE replies SET text = ?, edited = ?
                       WHERE reply_id = ?''', (merged.text, True, old_reply.id))
    
    return merged if (merged and edited) else None


def exists(reply_id: int) -> bool:
     
    reply = read_query('''SELECT reply_id FROM replies WHERE reply_id = ? LIMIT 1''', (reply_id,))
    
    return bool(reply)


def delete(reply_id: int, current_user: User) -> str | None:

    """
    Delete a reply from the database based on the given reply ID.

    Args:
        reply_id (int): The ID of the reply to be deleted.

    Returns:
        str | None: Returns 'reply deleted' if the deletion was successful, 
                    otherwise returns None.

    Raises:
        NotFoundException: If the reply with the given ID does not exist.
    """

    if not exists(reply_id):
        raise NotFoundException(detail='Reply not found')

    reply_username = read_query('''SELECT u.username from users u
                                JOIN replies r on r.user_id = u.user_id
                                WHERE r.reply_id = ?''', (reply_id,))

    if not current_user.is_admin:
        if current_user.username != reply_username[0][0]:
            raise ForbiddenException(detail='You are not allowed to delete this reply')
    
    deleted = update_query('''DELETE FROM replies WHERE reply_id = ?''', (reply_id,))
    
    return 'reply deleted' if deleted else None


def fetch_text(reply_id: int) -> str:

    reply_text_row = read_query('''SELECT text FROM replies WHERE reply_id = ?''', (reply_id,))

    return str(reply_text_row[0][0])