from typing import Annotated, Any

from fastapi_utils.cbv import cbv
from fastapi import APIRouter, Depends, Response, status, Cookie
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.api.deps import get_db
from .service import AuthService
from .schemas import Email

router = APIRouter()

@cbv(router)
class AuthRouter:
    session: Session = Depends(get_db)
    
    def _get_service(self) -> AuthService:
        return AuthService(self.session)
    
    @router.post("/verifyToken")
    def verifyToken(
        self,
        res: Response,
        access_token: Annotated[str | None, Cookie()] = None,
      ):
        print(access_token)
        self._get_service().verifyToken(res, access_token)
        res.status_code = status.HTTP_204_NO_CONTENT
    
    @router.post("/login/token")
    def login(self, 
              form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
              res: Response,
            ) -> Any:
         """
         OAuth2 compatible token login, get an access token for future requests
         """
         service = self._get_service().OAuth2PasswordAuth(res, form_data)
         res.status_code = status.HTTP_204_NO_CONTENT
    
    @router.get("/login/google")
    def googleLogin(self) -> Any:
        """
        Get Google OAuth login URL.
        """
        URL = self._get_service().generateGoogleOAuthLoginURI()
        return {"URL": URL}
    
    @router.get("/login/google/callback")
    def googleCallback(self, state: str, code: str) -> Any:
        """
        Get access token from Google and fetch user.
        
        Actual user login occurs here.
        """
        service = self._get_service()
        
        access_token = service.getGoogleAuthTokens(state=state, code=code)
        # User fecth and authentication process
        service.GoogleOAuthLogin(access_token=access_token)
    
    @router.post("/refreshToken")
    def refreshToken(
        self, 
        res: Response,
        refresh_token: Annotated[str | None, Cookie()] = None,
    ) -> Any:
        self._get_service().refreshAccessToken(res, refreshToken=refresh_token)
        res.status_code = status.HTTP_204_NO_CONTENT
    
    @router.post("/email-verification/request")
    def get_email_verification_link(self, email: Email, res: Response) -> Any:
        self._get_service().email_verification_request(email.email)
        res.status_code = status.HTTP_204_NO_CONTENT
    
    @router.post("email-verification/confirm")
    def verify_email(self, token: str, res: Response) -> Any:
        self._get_service().verify_email(token)
        res.status_code = status.HTTP_204_NO_CONTENT
        
        
        
    