from pydantic import BaseModel


class Vote(BaseModel):

    user_id: int
    reply_id: int
    type: bool

    @classmethod
    def from_query_result(cls, user_id, reply_id, type):
        return cls(user_id=user_id, reply_id=reply_id, type=type)