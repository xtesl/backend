from enum import Enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, String 
from pydantic import EmailStr

from src.models import Base
from src.institutions.models import Institution

# if TYPE_CHECKING:
#     from src.finance.models import Subscription

class AccountStatus(str, Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    DEACTIVATED = 'deactivated'

class APIAccountType(str, Enum):
    FREELANCER = "freelancer"
    EMPLOYER = "employer"
    
class AccountType(str, Enum):
    FREELANCER = "freelancer"
    EMPLOYER = "employer"
    ADMIN = "admin"


class UserBase(SQLModel):
    first_name: str = Field(nullable=False, sa_type=String(128))
    last_name: str = Field(nullable=False, sa_type=String(128))
    email: EmailStr = Field(unique=True, index=True, max_length=128)
    username: str = Field(index=True, unique=True, max_length=128)


class UserAccount(Base, UserBase, table=True):
    __tablename__ = "user_accounts"
    __tableprefix__ = "usacc"
    
    status: AccountStatus = Field(default=AccountStatus.ACTIVE)
    hashed_password: str = Field(max_length=255)
    type: AccountType
    is_email_verified: bool = False
    last_login: datetime | None = None 

"""Client data models"""

class Employer(Base, table=True):
    __tablename__ = "employers"
    __tableprefix__ = "emp"
    
    user_account_pk: str = Field(foreign_key="user_accounts.pk")
    location: str | None = Field(max_length=255, default=None)
    company_pk: str | None = Field(foreign_key="companies.pk", default=None)
    
    company: Optional["Company"] = Relationship(back_populates="employers")

class Company(Base, table=True):
    __tablename__ = "companies"
    __tableprefix__ = "cmp"
    
    comapany_name: str = Field(max_length=128)
    comapany_location: str = Field(max_length=225)
    
    employers: list[Employer] = Relationship(back_populates="company", cascade_delete=True)


"""Freelancer data models"""

class Freelancer(Base, table=True):
    __tablename__ = "freelancers"
    __tableprefix__ = "frl"
    
    user_account_pk: str = Field(foreign_key="user_accounts.pk")
    institution_pk: str = Field(foreign_key="institutions.pk")
    overview: str | None = Field(sa_type=String(), default=None)
    
    university: Institution = Relationship(back_populates="students")
    certifications: list["Certification"] = Relationship(back_populates="freelancer", 
                                                         cascade_delete=True)
    skills: list["HasSkill"] = Relationship(back_populates="freelancer", cascade_delete=True)
    
class Certification(Base, table=True):
    __tablename__ = "certifications"
    __tableprefix__ = "cert"
    
    certification_name: str = Field(max_length=255)
    provider: str = Field(max_length=255)
    description: str = Field(sa_type=String())
    certification_link: str | None = Field(sa_type=String(), default=None)
    freelancer_pk: str = Field(foreign_key="freelancers.pk")
    
    freelancer: Freelancer = Relationship(back_populates="certifications")
    

class HasSkill(Base, table=True):
    __tablename__ = "has_skills"
    __tableprefix__ = "hsskl"
    
    freelancer_pk: str = Field(foreign_key="freelancers.pk")
    skill_pk: str = Field(foreign_key="skills.pk")
    
    freelancer: Freelancer = Relationship(back_populates="skills")
    

 