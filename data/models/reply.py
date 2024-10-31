from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Reply(BaseModel):

    id: Optional[int] = None
    text: str = Field(..., min_length=1)
    user_id: int
    topic_id: int
    created: datetime = Field(default_factory=datetime.now)
    edited: Optional[bool] = Field(default=False)

    @classmethod
    def from_query_result(cls, id, text, user_id, topic_id, created, edited):
        return cls(id=id, text=text, user_id=user_id, topic_id=topic_id, created=created, edited=edited)

class ReplyResponse(BaseModel):

    id: int
    text: Optional[str] = None

    @classmethod
    def from_query_result(cls, id, text):
        return cls(id=id, text=text)

class ReplyEditID(BaseModel):

    id: int

class ReplyEdit(BaseModel):

    text: str = Field(..., min_length=1)

class ReplyCreate(BaseModel):

    text: str = Field(..., min_length=1)
    topic_id: int