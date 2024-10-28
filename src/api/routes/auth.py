from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.api.deps import SessionDep
from src.crud.user import authenticate, get_user_by_email
from src.models.security.data import Token
from src.models.user.schemas import AccountStatus
from src.models.generic.data import SimpleResponse, ResponseStatus
from src.core.security import create_access_token
from src.utils.helpers import (
    generate_email_verification_url,
    verify_jwt_token,
    generate_password_reset_url
)
from src.core.config import settings


router = APIRouter()


@router.post("/login/accessToken")
async def login_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate(session=session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # TODO: check for active and verified users
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.pk, expires_delta=access_token_expires
        )
    )

@router.post("/email/verificationURL")
async def get_email_verification_url(email: EmailStr) -> Any:
    """
    Returns a verification link for verification through the frontend.
    """
    url = generate_email_verification_url(email=email)
    return {"url": url}


@router.post(
    "/email/verification",
    response_model=SimpleResponse
)
async def verify_email(token: str, session: SessionDep) -> Any:
    email = verify_jwt_token(token=token)
    
    if not email:
        raise HTTPException(
            status_code=403,
            details="Invalid token"
        )
    
    user = get_user_by_email(session=session, email=email)
    
    # Change only .UNVERIFIED status
    if user.status is AccountStatus.UNVERIFIED:
        user.status = AccountStatus.ACTIVE
    
    # TODO: Change this structure when flow is clear.
    elif user.status is AccountStatus.ACTIVE:
        raise HTTPException(
            400,
            detail="Account already verified"
        )
    else:
        raise HTTPException(
            status_code=403,
            detail="Account can't be verified because of it's state."
        )
    
    session.add(user)
    session.commit()
    
    return SimpleResponse(status=ResponseStatus.SUCCESS, message="Email verified successfully")


@router.post("/reset-password")
async def get_password_reset_url(email: EmailStr) -> Any:
    url = generate_password_reset_url(email=email)
    
    return {"url": url}

    
    
    
    
    