from pydantic import BaseModel, Field, field_validator
from typing import Annotated

no_category = 1
PositiveInt = Annotated[int, Field(ge=1)]
ValidTitle = Annotated[str, Field(min_length=3)]

class Topic(BaseModel):
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
    topic_id: PositiveInt
    title: ValidTitle
    user_id: PositiveInt
    author: str
    status: bool = Field(alias='is_locked')
    best_reply_id: PositiveInt | None = None
    category_id: PositiveInt
    category_name: ValidTitle

    @classmethod
    def from_query(cls, topic_id, title, user_id, author, is_locked, best_reply_id, category_id, category_name):
        return cls(
            topic_id=topic_id,
            title=title,
            user_id=user_id,
            author=author,
            status='open' if is_locked == 1 else 'closed',
            best_reply_id=best_reply_id,
            category_id=category_id,
            category_name=category_name
        )

class TopicCreate(BaseModel):
    title: ValidTitle
    category_id: PositiveInt | None = no_category

class TopicUpdate(BaseModel):
    title: ValidTitle | None = None
    best_reply_id: PositiveInt


class TopicCategoryResponse(BaseModel):

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
