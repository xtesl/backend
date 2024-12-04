from typing import Annotated, Any, TypeVar, Callable, Optional, Type
from collections.abc import Generator

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from fastapi import Depends, HTTPException, status, Query, Request
from fastapi.security import OAuth2PasswordBearer


from src.core.db import engine
from src.core.config import settings
from src.core import security
from src.models import TokenPayload
from src.users.models import UserAccount, AccountType
from src.models import OffsetPagination
from src.jobs.models import Job
# from src.proposals.models import Proposal
# from src.models.institution.schemas import Institution
# from src.models.review.schemas import Review


T = TypeVar("T")

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/auth/login/token",
    auto_error=False
)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(session: SessionDep, request: Request) -> UserAccount:
    """
    Uses Cookies authentication for the authorization process.
    """
    try:
        token = request.cookies.get("access_token")
        
        payload = jwt.decode(
             token, settings.SECRET_KEY,
             algorithms=[security.ALGORITHM]
         )
        token_data = TokenPayload(**payload)
        
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
    user = session.get(UserAccount, token_data.sub)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

CurrentUser = Annotated[UserAccount, Depends(get_current_user)]

def get_normal_user(current_user: CurrentUser) -> UserAccount:
    """
    Filter for users with account types EMPLOYER and FREELANCER.
    """
    normal_account_types = [AccountType.FREELANCER, AccountType.EMPLOYER]
    if current_user.account_type not in normal_account_types:
        raise HTTPException(403, "User doesn't have enough privileges")
    return current_user
    
NormalUser = Annotated[UserAccount, Depends(get_normal_user)]

def get_employer(current_user: CurrentUser) -> UserAccount:
    """
    Return users with account type of employer, otherwise raise HTTPException
    """
    if current_user.account_type is AccountType.EMPLOYER:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User doesn't have enough privileges"
    )

CurrentEmployerUser = Annotated[UserAccount, Depends(get_employer)]

def get_freelancer(current_user: CurrentUser) -> UserAccount:
    if current_user.account_type is AccountType.FREELANCER:
        return current_user
    raise HTTPException(
        status_code=403,
        detail="User doesn't have enough privileges"
    )


def offset_pagination_params(
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of items to return (between 1 and 100)"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of items to skip (0 or greater)"
    )
) -> OffsetPagination:
    return OffsetPagination(offset=offset, limit=limit)

OffsetPaginationParams = Annotated[OffsetPagination, Depends(offset_pagination_params)]




    
        