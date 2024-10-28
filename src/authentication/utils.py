from datetime import timedelta, timezone
from datetime import datetime
from typing import Any

from sqlmodel import Session
from pydantic import EmailStr
from passlib.context import CryptContext
from fastapi import HTTPException
import jwt
from jwt.exceptions import InvalidTokenError

from src.users.models import UserAccount
from src.utils.db import get_object_or_404
from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def generate_jwt_token(sub: str| Any, duration: timedelta) -> str:
    expire = datetime.now(timezone.utc) + duration
    
    endcoded_jwt = jwt.encode(
        {"sub": str(sub), "nbf": datetime.now(), "exp": expire},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    
    return endcoded_jwt


def verify_jwt_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        return str(decoded_token["sub"]) 
    
    except InvalidTokenError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate(session: Session, email: EmailStr, password: str) -> UserAccount:
    user = get_object_or_404(session, UserAccount.email, email, False)
    if user:
        hashed_password = user.hashed_password
        if not verify_password(password, hashed_password):
            return None
        return user
    return None


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt