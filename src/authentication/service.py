from typing import Any
from datetime import timedelta

from sqlmodel import Session
from fastapi import HTTPException
from pydantic import EmailStr

from .utils import authenticate, create_access_token, verify_jwt_token, generate_jwt_token
from src.users.models import AccountStatus, UserAccount
from src.models import Token
from src.core.config import settings
from src.utils.db import get_object_or_404, save, get_object_with_pk_or_404
from src.utils.helpers import send_email, render_email_template


class AuthService:
    def __init__(self, session: Session):
        self.session = session
    
    
    def OAuth2PasswordAuth(self, form_data: Any) -> Token:
        """
        OAuth2 Password flow authentication.
        """
        user = authenticate(self.session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(400, "Invalid credentials")
        # Users with account statuses of suspended and deactivated can't login
        not_allowed_statuses = [AccountStatus.SUSPENDED, AccountStatus.DEACTIVATED]
        if user.status in not_allowed_statuses:
            raise HTTPException(403, "Account not active") 
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return Token(
            access_token=create_access_token(
                user.pk,
                access_token_expires
            ),
        )
    
    def verify_email(self, token: str) -> None:
        user_pk = verify_jwt_token(token)
        if user_pk:
            user = get_object_with_pk_or_404(user_pk, self.session, UserAccount)
            if user.is_verified_email:
                raise HTTPException(403, "Email already verified")
            user.is_verified_email = True
            save(self.session, user)
            
        raise HTTPException(400, "Invalid token")
    
    def email_verification_request(self, email: EmailStr) -> None:
        user = get_object_or_404(self.session, UserAccount.email, email)
        duration = timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
        token = generate_jwt_token(sub=user.pk, duration=duration)
        
        # Render template to send email
        send_email(
            email_to=email,
            subject="Email verification",
            html_content=render_email_template(
                template_name="email_verification",
                context={"token": token}
            )
        )
        
        