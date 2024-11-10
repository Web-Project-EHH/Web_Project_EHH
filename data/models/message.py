
from pydantic import BaseModel, Field
from data.models.topic import PositiveInt

class Message(BaseModel):
    """
    Message model for the database
    Parameters:
    message_id: PositiveInt - The unique identifier for the message
    text: str - The text of the message (min length 2)
    sender_id: PositiveInt - The unique identifier for the sender
    receiver_id: PositiveInt - The unique identifier for the receiver
    """
    message_id: PositiveInt
    text: str = Field(..., min_length=2)
    sender_id: PositiveInt
    receiver_id: PositiveInt

    @classmethod
    def from_query(cls, row):
        message_id, text, sender_id, receiver_id = row
        return cls(
            message_id=message_id,
            text=text,
            sender_id=sender_id,
            receiver_id=receiver_id
            )

class MessageText(BaseModel):
    """
    Message text model for the database
    Parameters:
    text: str - The text of the message (min length 1)
    """
    text: str = Field(..., min_length=1)

class MessageCreate(BaseModel):
    text: str
    sender_id: int
    receiver_id: int