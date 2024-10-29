from unittest.mock import MagicMock
from data.models.category import Category
from data.models.reply import Reply
from data.models.user import User


def mock_category(id, name, is_locked, is_private):
    category = MagicMock(spec=Category)
    category.id = id
    category.name = name
    category.is_locked = is_locked
    category.is_private = is_private
    
    return category

def mock_reply(id, text, user_id, topic_id, created, edited):
    reply = MagicMock(spec=Reply)
    reply.id = id
    reply.text = text
    reply.user_id = user_id
    reply.topic_id = topic_id
    reply.created = created
    reply.edited = edited

    return reply

def mock_user(id, username, password, email,first_name,
               last_name, created_at, is_admin, is_deleted):
    
    user = MagicMock(spec=User)
    user.id = id
    user.username = username
    user.password = password
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.created_at = created_at
    user.is_admin = is_admin
    user.is_deleted = is_deleted

    return user
