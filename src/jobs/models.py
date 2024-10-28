from sqlmodel import Field, Relationship, SQLModel, String, Column, ARRAY
from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from src.models import Base

if TYPE_CHECKING:
    from src.proposals.models import Proposal

class ExpectedDuration(Base, table=True):
    """Expected duration for job"""
    __tablename__ = "expected_durations"
    __tableprefix__ = "exp_dur"
    
    duration_text: str = Field(max_length=255, unique=True)

class Complexity(Base, table=True):
    __tablename__ = "complexities"
    __tableprefix__ = "cmplx"
    
    complexity_text: str = Field(max_length=255, unique=True)

class Skill(Base, table=True):
    __tablename__ = "skills"
    __tableprefix__ = "skl"
    
    skill_name: str = Field(max_length=128)

class PaymentType(str, Enum):
    PER_HOUR = "per_hour"
    FIXED_PRICE = "fixed_price"
    
class OtherSkills(Base, table=True):
    __tablename__ = "other_skills"
    __tableprefix__ = "othskl"
    
    job_pk: str = Field(foreign_key="jobs.pk")
    skill_pk: str = Field(foreign_key="skills.pk")
    
    job: "Job" = Relationship(back_populates="other_skills")
    
class Job(Base, table=True):
    __tablename__ = "jobs"
    __tableprefix__ = "jb"
    
    employer_pk: str = Field(foreign_key="employers.pk")
    expected_duration: str = Field(foreign_key="expected_durations.pk")
    complexity_pk: str = Field(foreign_key="complexities.pk")
    main_skill_pk: str = Field(foreign_key="skills.pk")
    description: str = Field(sa_type=String())
    payment_type: PaymentType
    payment_amount: Decimal = Field(max_digits=8, decimal_places=2)
    
    other_skills: list[OtherSkills] = Relationship(back_populates="job", cascade_delete=True)
    proposals: list["Proposal"] = Relationship(back_populates="job", cascade_delete=True)
    

 