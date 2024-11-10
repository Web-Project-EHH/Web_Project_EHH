import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):

    """
    Represents a user in the system.

    Attributes:
        id (Optional[int]): The unique identifier of the user.
        username (str): The username of the user.
        password (str): The password of the user.
        email (EmailStr): The email address of the user.
        first_name (Optional[str]): The first name of the user.
        last_name (Optional[str]): The last name of the user.
        created_at (Optional[datetime.datetime]): The timestamp when the user was created.
        is_admin (bool): Indicates if the user has admin privileges.
        is_deleted (bool): Indicates if the user is deleted.
        bio (Optional[str]): The biography of the user.
    """ 

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

    """
    Represents the login information for a user.
    """ 
    id: Optional[int] = None
    username: str = Field(..., min_length=2, max_length=20)
    password: str 
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None




class UserRegistration(BaseModel):

    """
    Represents the registration information for a new user.
    """
    username: str = Field(..., min_length=2, max_length=20)
    password: str   
    confirm_password: str
    email: EmailStr
    first_name: str
    last_name: str
    is_admin: bool = False
    

class UserResponse(BaseModel):

    """
    Represents the response data for a user.
    """
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

        """
        Creates a UserResponse instance from a query result.

        Args:
            query_result (tuple): The result of a database query.

        Returns:
            UserResponse: An instance of the UserResponse class.
         """
        return cls(
            id=query_result[0],
            username=query_result[1],
            email=query_result[3],
            first_name= query_result[4],
            last_name= query_result[5],
            is_admin= query_result[6],
        )

class TokenResponse(BaseModel):

    """
    Represents the token response for authentication.

    Attributes:
        access_token (str): The access token.
        token_type (str): The type of the token.
    """
    access_token: str
    token_type: str


class UserInfo(BaseModel):

    """
    Represents the basic information of a user.
    """
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @classmethod
    def from_query_result(cls, username, email, first_name, last_name):

        """
        Creates a UserInfo instance from a query result.

        Returns:
            UserInfo: An instance of the UserInfo class.
        """
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
