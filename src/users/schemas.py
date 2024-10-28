from datetime import datetime

from sqlmodel import Field, SQLModel, String
from pydantic import EmailStr

from .models import (
    AccountType,
    APIAccountType, 
    Company,
    UserBase
)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    
class UserPublic(UserBase):
    type: AccountType
    pk: str
    status: str
    is_email_verified: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

class UserPublicWithTypeDetails(UserPublic):
    type_details: "EmployerPublic"

# class UsersPublicWithProfiles(SQLModel):
#     data: list[UserPublicWithProfile]
#     count: int

class EmployerPublic(SQLModel):
    company: Company | None
    location: str | None
    


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=105)
    username: str | None = Field(default=None, max_length=105)
    email: EmailStr | None = Field(default=None, max_length=255)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# class ProfilePublic(ProfileBase):
#     pass

# class UpdateProfile(SQLModel):
#     profile_image: str | None = Field(default=None, sa_column=String())
#     bio: str | None = Field(default=None, sa_type=String())
#     company_name: str | None = Field(default=None, sa_type=String(150)) 
#     company_website: str | None = None
#     name: str | None = None
#     location: str | None = None
#     program: str | None = None

# class ProfilePublicFreelancer(SQLModel):
#     profile_image: str | None = Field(default=None, sa_column=String)
#     bio: str | None = Field(default=None,  sa_type=String())
#     program: str | None = None

# class ProfilePublicEmployer(SQLModel):
#     profile_image: str | None = Field(default=None, sa_column=String())
#     bio: str | None = Field(default=None, sa_type=String())
#     company_name: str | None = Field(default=None, sa_type=String(150)) 
#     company_website: str | None = None
#     name: str | None = None
#     location: str | None = None
    
    
    
