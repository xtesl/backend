from typing import TYPE_CHECKING
from sqlmodel import Field
from sqlalchemy import String, Enum as SQLAlchemyEnum
from enum import Enum
from datetime import datetime

from src.models import Base

if TYPE_CHECKING:
    pass

class Status(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class Dispute(Base, table=True):
    __tablename__ = "disputes"
    __tableprefix__ = "dsp"
    reason: str = Field(sa_type=String(500))
    status: Status = Field(SQLAlchemyEnum(Status))
    resolution: str = Field(sa_type=String(500))
    resolved_at: datetime | None = None