

from sqlmodel import SQLModel
from pydantic import EmailStr




class Email(SQLModel):
    email: EmailStr
    