from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from data.database import read_query, insert_query, update_query
from data.models.reply import Reply
from typing import List
from common.exceptions import ConflictException, NotFoundException, ForbiddenException

def get_replies(reply_id: int = None, text: str = None, user_id: int = None, user_name: str = None,
                topic_id: int = None, topic_title: str = None, sort_by: str = None, sort: str = None,
                start_date: datetime = None, end_date: datetime = None, limit: int = 10,
                offset: int = 0) -> List[Reply] | Reply:
    
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
        topic_id_row = read_query('''SELECT t.topic_id FROM topics t JOIN replies r ON t.topic_id = r.topic_id WHERE t.topic_title = ? LIMIT 1''', (topic_title,)) if topic_title else None
        topic_id = topic_id_row[0][0] if topic_id_row else topic_id
        query += ''' AND topic_id = ?'''
        params.append(topic_id)

    if start_date:
        query += '''AND created > ?'''
        params.append(start_date)

    if end_date:
        query += '''AND created < ?'''
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
    
    

def two_replies_exist(reply_text: int) -> bool:

    replies = read_query('''SELECT COUNT(*) FROM replies WHERE text = ? LIMIT 2''', (reply_text,))

    return True if replies[0][0] == 2 else False
    

def create(reply: Reply) -> Reply | HTTPException | None:

    if two_replies_exist:
        raise ForbiddenException('Cannot post the same reply more than twice')
    
    generated_id = insert_query('''INSERT INTO replies (text, user_id, topic_id, created, edited) VALUES (?, ?, ?, ?, ?)''',
                                (reply.text, reply.user_id, reply.topic_id, reply.created, reply.edited))
    
    reply.id = generated_id

    return reply if reply else None

