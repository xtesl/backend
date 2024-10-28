from sqlmodel import (
    SQLModel,
    Field,
    Relationship, 
    String,
    ARRAY, 
    Column
)
from enum import Enum
from typing import List, TYPE_CHECKING

from src.models import Base
if TYPE_CHECKING:
    from src.users.models import Freelancer

class Category(Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class Institution(Base, table=True):
    """
    University institutions in Ghana.
    """
    __tablename__ = "institutions"
    __tableprefix__ = "ins"
    
    name: str = Field(index=True, unique=True)
    nick: str | None = Field(default=None, unique=True, index=True)
    # Just Ghanaian locations to campuses.
    # Should be formatted by frontend when displayed
    campuses: List[str] = Field(sa_column=Column(ARRAY(String)))
    category: Category
    
    students: list["Freelancer"] = Relationship(back_populates="university", cascade_delete=True)
    
 