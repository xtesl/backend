from sqlmodel import SQLModel, Field, String, Column, ARRAY
from datetime import datetime
from decimal import Decimal
from typing import List

from .models import JobStatus, JobBase

class JobCreate(JobBase):
    pass

class JobPublic(JobBase):
    status: JobStatus
    pk: str

class JobsPublic(SQLModel):
    data: list[JobPublic]
    count: int

class JobUpdate(SQLModel):
    title: str | None = Field(sa_type=String(105), default=None)
    description: str | None = Field(sa_type=String(), default=None)
    deadline: datetime | None = None
    budget: Decimal | None = Field(max_digits=5, decimal_places=2, default=None)
    # Note: PostgreSQL feature
    tags: List[str] | None = Field(sa_column=Column(ARRAY(String)), default=None)
    required_skills: List[str] | None = Field(sa_column=Column(ARRAY(String)), default=None)
