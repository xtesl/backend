from sqlmodel import Field, Relationship
from sqlalchemy import String
from typing import TYPE_CHECKING


from src.models import Base

if TYPE_CHECKING:
    from src.users.models import  User
    

class Notification(Base, table=True):
    __tablename__ = "notifications"
    __tableprefix__ = "not"
    
    message: str = Field(sa_type=String())
    is_read: bool = False
    
    user_pk: str = Field(foreign_key="users.pk")
    user: "User" = Relationship(back_populates="notifications")
    