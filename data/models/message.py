from pydantic import BaseModel, Field
from data.models.topic import PositiveInt, ValidTitle

class Message(BaseModel):
    message_id: PositiveInt
    text: str = Field(..., min_length=2)
    sender_id: PositiveInt
    receiver_id: PositiveInt

    @classmethod
    def from_query(cls, message_id, text, sender_id, receiver_id):
        return cls(
            message_id=message_id,
            text=text,
            sender_id=sender_id,
            receiver_id=receiver_id
            )

    class MessageText(BaseModel):
        text: str = Field(..., min_length=1)
