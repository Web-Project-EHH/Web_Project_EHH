from typing import Optional
from pydantic import BaseModel, Field

class Category(BaseModel):

    id: Optional[int] = None
    name: str = Field(min_length=2, max_length=30, description='Category name must be between 2 and 30 characters')
    is_locked: bool
    is_private: bool

    @classmethod
    def from_query_result(cls, id, name, is_locked, is_private):
        return cls(id=id, name=name, is_locked=is_locked, is_private=is_private)
    
class CategoryResponse(BaseModel):
    
    id: Optional[int] = None
    name: Optional[str] = None

    @classmethod
    def from_query_result(cls, id, name):
        return cls(id=id, name=name)
    
class CategoryCreate(BaseModel):
    
    name: str = Field(min_length=2, max_length=30, description='Category name must be between 2 and 30 characters')
    is_locked: bool = False
    is_private: bool = False

    @classmethod
    def from_query_result(cls, id, name, is_locked, is_private):
        return cls(id=id, name=name, is_locked=is_locked, is_private=is_private)
    
class CategoryChangeNameID(BaseModel):

    id: int

class CategoryChangeName(BaseModel):

    name: str = Field(min_length=2, max_length=30, description='Category name must be between 2 and 30 characters')