from pydantic import BaseModel, Field, field_validator
from typing import Annotated

NO_CATEGORY = 1
PositiveInt = Annotated[int, Field(ge=1)]
ValidTitle = Annotated[str, Field(min_length=3)]


class Topic(BaseModel):
    """
    Topic model for creating a new topic
    It has the following fields:
    - topic_id: int - the id of the topic
    - title: str - the title of the topic
    - user_id: int - the user id of the topic creator
    - status: bool - the status of the topic (open or closed)
    - best_reply_id: int - the id of the best reply to the topic (if any)
    - category_id: int - the id of the category the topic belongs
    """
    topic_id: PositiveInt
    title: ValidTitle
    user_id: PositiveInt
    status: bool = Field(alias='is_locked')
    best_reply_id: PositiveInt | None = None
    category_id: PositiveInt

    @field_validator('status', mode='before')
    def validate_status(cls, value):
        if value == 1:
            return 'open'
        elif value == 0:
            return 'closed'
        raise ValueError('Status must be 0 or 1')


class TopicResponse(BaseModel):
    """
    Topic model for returning a topic from the database
    It has the following fields:
    - topic_id: int - the id of the topic
    - title: str - the title of the topic
    - user_id: int - the user id of the topic creator
    - author: str - the name of the topic creator
    - is_locked: bool - the status of the topic (open or closed)
    - best_reply_id: int - the id of the best reply to the topic (if any)
    - category_id: int - the id of the category the topic belongs
    - category_name: str - the name of the category the topic belongs
    """
    topic_id: PositiveInt
    title: ValidTitle
    user_id: PositiveInt
    author: str
    is_locked: bool
    best_reply_id: PositiveInt | None = None
    category_id: PositiveInt
    category_name: ValidTitle

    @classmethod
    def from_query(cls, topic_id, title, user_id, author,is_locked, best_reply_id, category_id, category_name):
        return cls(
            topic_id=topic_id,
            title=title,
            user_id=user_id,
            author=author,
            is_locked=bool(is_locked),
            best_reply_id=best_reply_id,
            category_id=category_id,
            category_name=category_name
        )


class TopicCreate(BaseModel):
    """
    Topic model for creating a new topic with no category
    It has the following fields:
    - title: str - the title of the topic
    - text: str - the content of the topic
    - category_id: int - the id of the category the topic belongs
    """
    title: ValidTitle
    text: str = Field(..., min_length=3)
    category_id: PositiveInt | None = NO_CATEGORY


class TopicBestReplyUpdate(BaseModel):
    """
    Topic model for updating the best reply of a topic
    It has the following fields:
    - best_reply_id: int - the id of the best reply to the topic
    """
    best_reply_id: PositiveInt


class TopicCategoryResponseUser(BaseModel):
    """
    Topic model for returning a topic from the database for user
    It has the following fields:
    - topic_id: int - the id of the topic
    - title: str - the title of the topic
    - user_id: int - the user id of the topic creator
    - best_reply_id: int - the id of the best reply to the topic (if any)
    - category_id: int - the id of the category the topic belongs
    """
    topic_id: int
    title: str
    user_id: int
    best_reply_id: int | None = None
    category_id: int

    @classmethod
    def from_query(cls, topic_id, title, user_id, best_reply_id, category_id):
        return cls(
            topic_id=topic_id,
            title=title,
            user_id=user_id,
            best_reply_id=best_reply_id,
            category_id=category_id,
        )


class TopicCategoryResponseAdmin(BaseModel):
    """
    Topic model for returning a topic from the database for admin
    It has the following fields:
    - topic_id: int - the id of the topic
    - title: str - the title of the topic
    - user_id: int - the user id of the topic creator
    - is_locked: bool - the status of the topic (open or closed)
    - best_reply_id: int - the id of the best reply to the topic (if any)
    - category_id: int - the id of the category the topic belongs
    """
    topic_id: int
    title: str
    user_id: int
    is_locked: bool
    best_reply_id: int | None = None
    category_id: int

    @classmethod
    def from_query(cls, topic_id, title, user_id, is_locked, best_reply_id, category_id):
        return cls(
            topic_id=topic_id,
            title=title,
            user_id=user_id,
            is_locked=is_locked,
            best_reply_id=best_reply_id,
            category_id=category_id,
        )