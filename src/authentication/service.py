from typing import Any
from datetime import timedelta

from sqlmodel import Session
from fastapi import HTTPException, status, Response
from pydantic import EmailStr

from .utils import authenticate, create_token, verify_jwt_token, generate_jwt_token
from src.users.models import AccountStatus, UserAccount
from src.models import Tokens
from src.core.config import settings
from src.utils.db import get_object_or_404, save, get_object_with_pk_or_404
from src.utils.helpers import send_email, render_email_template, make_request


class AuthService:
    def __init__(self, session: Session):
        self.session = session
    
    def getGoogleAuthTokens(self, state: str, code: str) -> str | None:
        """
        Gets users' access and refresh tokens
        
        Args:
            code: Authorization code from google upon successful login.
            state: state string used in the login string (from us).
        """
        # Validate state
        if settings.STATE == state:
            GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
            
            # Request body
            data = {
               "code": code,
               "client_id": settings.GOOGLE_CLIENT_ID,
               "client_secret": settings.GOOGLE_CLIENT_SECRET,
               "redirect_url": settings.GOOGLE_OAUTH_REDIRECT_URL,
               "grant_type": "authorization_code",
            }
            
            # Initiate request
            try:
                response_data = make_request(
                   method="POST",
                   url=GOOGLE_TOKEN_ENDPOINT,
                   data=data
                )
                
                return response_data["access_token"]
            
            except RuntimeError as e:
                return None
    
    def GoogleOAuthLogin(self, access_token: str) -> Any:
        """
        Fetchs user info and authenticates user.
        """
        try:
            URL = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response_data = make_request(
                   method="GET",
                   url=URL,
                   headers=headers
                )
            
            access_token = response_data["access_token"]
          
        except RuntimeError as e:
            return None
    
    def generateGoogleOAuthLoginURI(self) -> str:
        """
        Generate Google OAuth Login URL.
        """
        base = "https://accounts.google.com/o/oauth2/auth"
        
        # Query parameters
        client_id = settings.GOOGLE_CLIENT_ID
        redirect_url = settings.GOOGLE_OAUTH_REDIRECT_URL
        state = settings.STATE
        response_type = "code"
        scope = """
        https://www.googleapis.com/auth/userinfo.email 
        https://www.googleapis.com/auth/userinfo.profile
        """
        access_type = "offline"
        prompt = "consent"
        
        query_params = {
            "?client_id": client_id,
            "&redirect_uri": redirect_url,
            "&response_type": response_type,
            "&scope": scope.strip(),
            "&state": state,
            "&access_type": access_type,
            "&prompt": prompt
        }
        
        # Generate full URL from query params
        URL = base
        for name, value in query_params.items():
            URL += name + "=" + value
        
        return URL
        
    
    def verifyToken(self, res: Response, token: str | None) -> None:
        """
        Verify both access and refresh tokens.
        """
        if not token:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or missing"
            )
            
        decoded_token = verify_jwt_token(token)
        
        if decoded_token:
            return decoded_token
        else:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
       
    def refreshAccessToken(self, res: Response, refreshToken: str | None) -> None:
        """
        Refresh access tokens when refresh token is valid.
        """
        decoded_token = self.verifyToken(res=res, token=refreshToken)
        
        if decoded_token:
            # Refresh access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            res.set_cookie(
             key="access_token",
             value=create_token(
                decoded_token['sub'],
                access_token_expires,
                type="access",
            ),
             httponly=True,
             max_age=3600 # cookie expires in 1hr
         )
            
    
    def OAuth2PasswordAuth(self, res: Response, form_data: Any) -> None:
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
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        tokens = Tokens(
            access_token=create_token(
                user.pk,
                access_token_expires,
                type="access",
            ),
            refresh_token=create_token(
                user.pk,
                refresh_token_expires,
                type="refresh",
            )
        )
        
        # Authentication credentials set as httponly cookies
        res.set_cookie(
             key="access_token",
             value=tokens.access_token,
             httponly=True,
             max_age=3600 # cookie expires in 1hr
         )
        res.set_cookie(
             key="refresh_token",
             value=tokens.refresh_token,
             httponly=True,
             max_age=3600 * 24 * 7 # cookie expires in 1 week
         )
         
    
    def verify_email(self, token: str) -> None:
        user_pk = verify_jwt_token(token)
        if user_pk:
            user = get_object_with_pk_or_404(user_pk, self.session, UserAccount)
            if user.is_verified_email:
                raise HTTPException(403, "Email already verified")
            user.is_verified_email = True
            save(self.session, user)
            
        raise HTTPException(401, "Invalid token")
    
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
        
        