import uuid
from datetime import datetime
from typing import Any
from enum import Enum

from sqlmodel import SQLModel, Field, String

class Base(SQLModel):
    """
    Extend this model class for theses fields: `created_at`: datetime, 
    `updated_at`: datetime 
    and `pk`: str.
    """
    __tableprefix__: str = "" 
    
    pk: str | None = Field(
        default_factory=lambda: f"{Base.__tableprefix__}_{uuid.uuid4()}",
        primary_key=True,
        sa_type=String(105)
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
    

# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


from sqlmodel import SQLModel

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class SimpleResponse(SQLModel):
    status: ResponseStatus
    message: str | None

class PaginationResponse(SQLModel):
    data: list[Any]
    pagination: dict

class OffsetPagination(SQLModel):
    offset: int = 0,
    limit: int = 10
    