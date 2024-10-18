from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class Category(BaseModel):

    id: Optional[int] = None
    name: str = Field(min_length=2, max_length=30, description='Category name must be between 2 and 30 characters')
    is_locked: bool
    is_private: bool

    @classmethod
    def from_query_result(cls, id, name, is_locked, is_private):
        return cls(id=id, name=name, is_locked=is_locked, is_private=is_private)
    
class CategoryResponse(BaseModel):
    
    id: int
    name: str

    @classmethod
    def from_query_result(cls, id, name):
        return cls(id=id, name=name)