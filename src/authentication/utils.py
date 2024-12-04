from datetime import timedelta, timezone
from datetime import datetime
from typing import Any, Literal

from sqlmodel import Session
from pydantic import EmailStr
from passlib.context import CryptContext
from fastapi import HTTPException, Response
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


def set_del_auth_credentials(
    response: Response,
    token_type: Literal["access_token", "refresh_token"],
    operation: Literal["set", "delete"] = "set",
    token_data: str | None = None,
    ) -> None:
    """
    Generates and sets authentication tokens as HTTP-Only cookies.
    
    Can also be used for logout process, where you need to delete
    authentication credentials.
    
    Args:
      token_type: Authentication token type (`access_token`, `refresh_token`).When wrong type is 
                  passed, `access_token` type will be used.
      
      response: The HTTP response object to set the cookies on.
      
      token_data: User's data to be used for the JWT token generation i.e sub
      
      operation: Operation to be performed, to delete token or set token.
      returns: `None`
    """
    # Delete token
    if operation == "delete":
        response.delete_cookie(
            key=token_type,
            httponly=True,
        )
        
        return
        
    # Tokens expire times
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
      
    expire_times = {
          "access_token": access_token_expires,
          "resfresh_token": refresh_token_expires
        }
    
    
    # Select token expiration time
    try:
        expire_time = expire_times[token_type]
    except KeyError:
        token_type = "access_token"
        expire_time = expire_times[token_type]
    
    token = create_token(
                token_data,
                expire_time,
                type=token_type,
            )
    
    response.set_cookie(
        key=token_type,
        value=token,
        httponly=True,
        max_age=expire_time * 60 # Convert from minutes to seconds
    )

      

def verify_jwt_token(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        return decoded_token
    
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


def create_token(subject: str | Any, expires_delta: timedelta, type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "token_type": type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt