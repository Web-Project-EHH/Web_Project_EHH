from pydantic import BaseModel, Field, EmailStr

class Category(BaseModel):

    id: int = None
    name: str
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