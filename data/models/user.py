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
    bio: Optional[str] = None  # Add bio field

    @classmethod
    def from_query(cls, **kwargs):
        return cls(**kwargs)
    

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


class UserSearch(BaseModel):
    username: str

    @classmethod
    def from_query_result(cls, query_result):
        return cls(
            username=query_result[0]
        )
    

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: bool = False
    is_deleted: bool = False
    bio: Optional[str] = None

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

class UserProfileUpdate(BaseModel):
    """Model for updating user profile information"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)  # Limit bio length
    new_password: Optional[str] = None
    confirm_password: Optional[str] = None

# class AnonymousUser(BaseModel):
#     raise NotImplementedError
# DA OBSDUIM DALI SHTE GO POLZVAME
