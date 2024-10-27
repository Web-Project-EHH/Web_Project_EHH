from __future__ import annotations
from data.models.topic import PositiveInt

from data.models.topic import TopicResponse, TopicCreate
from data.database import read_query, update_query, insert_query, query_count
from mariadb import IntegrityError
from starlette.requests import Request

DEFAULT_BEST_REPLY_NONE = None

def exists(topic_id: PositiveInt):
    return any(read_query('''SELECT 1 FROM topics WHERE topic_id=?''', (id,)))


def fetch_all_topics(
        search: str = None,
        username: str = None,
        category: str = None,
        status: str = None,
        sort: str = None,
        sort_by: str = None
    ):
    params, filters = (), []
    sql = (
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
        FROM topics t
        JOIN users u ON t.user_id = u.user_id
        JOIN categories c ON t.category_id = c.category_id '''
    )

    if search:
        filters.append('t.title LIKE ?')
        params += (f'%{search}%',)
    if username:
        filters.append('u.username = ?')
        params += (username,)
    if category:
        filters.append('c.name = ?')
        params += (category,)
    if status:
        filters.append('t.is_locked = ?')
        params += (1 if status == 'open' else 0)

    sql += (" WHERE " + " AND ".join(filters) if filters else "")

    if sort and sort != 'topic_id':
        if sort_by == 'user_id':
            sort_by = 't.user_id'
        elif sort_by == 'category_id':
            sort_by = 't.category_id'
        elif sort_by == 'status':
            sort_by = 't.is_locked'

        sql += f' ORDER BY {sort_by} IS NULL, {sort_by} {sort.upper()}'

    data = read_query(sql, params)
    topics = [TopicResponse.from_query(*row) for row in data]

    return topics


def fetch_topic_by_id(topic_id: PositiveInt) -> TopicResponse | None:
     data = read_query(
         '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name\n
              FROM topics t\n
              JOIN users u ON t.user_id = u.user_id\n
              JOIN categories c ON t.category_id = c.category_id WHERE t.topic_id = ?''', (topic_id,))

     return next((TopicResponse.from_query(*row) for row in data), None)


def create_new_topic(topic: TopicCreate, user_id: PositiveInt):
    try:
        new_topic_id = insert_query(
            '''INSERT INTO topics(title, user_id, is_locked, best_reply_id, category_id) VALUES(?,?,?,?,?)''',
            (topic.title, user_id, 1, DEFAULT_BEST_REPLY_NONE, topic.category_id)
        )
        return {
            'topic_id': new_topic_id,
            'title': topic.title,
            'user_id': user_id,
            'is_locked': 1,
            'best_reply_id': DEFAULT_BEST_REPLY_NONE,
            'category_id': topic.category_id
        }
    except IntegrityError as e:
        return None

def update_topic_title(topic_id, new_title):
    update_query('''UPDATE topics SET title = ? WHERE topic_id = ?''', (new_title, topic_id))

    return f"Topic {topic_id} title updated to {new_title}"


def update_best_reply_for_topic(topic_id, reply_id):
    update_query('''UPDATE topics SET best_reply_id = ? WHERE topic_id = ?''', (reply_id, topic_id))

    return f"Best reply for topic {topic_id} updated to {reply_id}"

def fetch_replies_for_topic(topic_id):
    data = read_query(
        '''SELECT r.reply_id, r.content, r.user_id, u.username, r.topic_id, r.created_at
        FROM replies r '
        JOIN users u ON r.user_id = u.user_id
        WHERE r.topic_id = ?''',
        (topic_id,)
    )
    return data

def check_topic_access_permissions(user_id, topic_id):
    existing_topic = fetch_topic_by_id(topic_id)

    if not existing_topic:
        return False, f"Topic #ID:{topic_id} doest not exists!"

    if existing_topic.user_id != user.user_id:
        return False, 'You are not allowed to edit this topic.'

    if existing_topic.status == 'closed':
        return False, 'This topic is locked'

#трябва да опправя locked/closed.

#ДА ИМПОРТНА ЮЗЪР ОТ ЕЛИЦА И ДА СИ ДОВЪРША КОДА
    if existing_topic.user_id != user.user_id:
        return False, 'You are not allowed to edit topics that does not belong to you.'

    if existing_topic.status == "closed":
        return False, 'Topic is closed.'

    return True, 'OK'

def lock_or_unlock_topic(topic_id, lock_status: bool):
    update_query('''UPDATE topics SET is_locked = ? WHERE topic_id = ?''',
                 (lock_status, topic_id))

def verify_topic_owner(user_id, topic_id):
    data = read_query('''SELECT FROM topics = ? WHERE topic_id = ? AND user_id = ?''',
                      (topic_id, user_id))

    if not data:
        return False
    return True


