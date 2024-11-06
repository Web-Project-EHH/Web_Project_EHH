import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., min_length=2, max_length=50)
    password: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    is_admin: bool = False
    is_deleted: bool = False
    
    @classmethod
    def from_query_result(cls, id, username, password, email, first_name, last_name, created_at , is_admin, is_deleted):
        return cls(
            id=id,
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            created_at=created_at,
            is_admin=is_admin,
            is_deleted=is_deleted
        )
    

class UserLogin(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., min_length=2, max_length=20)
    password: str 
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserRegistration(BaseModel):
    username: str = Field(..., min_length=2, max_length=20)
    password: str   
    confirm_password: str
    email: EmailStr
    first_name: str
    last_name: str
    is_admin: bool = False
    

class UserResponse(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., min_length=2, max_length=20)
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: bool = False

    @classmethod
    def from_query_result(cls, query_result):
        return cls(
            id=query_result[0],
            username=query_result[1],
            email=query_result[3],
            first_name= query_result[4],
            last_name= query_result[5],
            is_admin= query_result[6],
        )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserInfo(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @classmethod
    def from_query_result(cls, username, email, first_name, last_name):
        return cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
    

class UserAuthDep(BaseModel):
    user_id: Optional[int] = None      

# class AnonymousUser(BaseModel):
#     raise NotImplementedError
# DA OBSDUIM DALI SHTE GO POLZVAME
