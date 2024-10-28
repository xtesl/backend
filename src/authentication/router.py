from typing import Annotated, Any

from fastapi_utils.cbv import cbv
from fastapi import APIRouter, Depends, Response, status
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
    
    @router.post("/login/token")
    def login(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Any:
         """
         OAuth2 compatible token login, get an access token for future requests
         """
         service = self._get_service()
         return service.OAuth2PasswordAuth(form_data)
    
    @router.post("/email-verification/request")
    def get_email_verification_link(self, email: Email, res: Response) -> Any:
        self._get_service().email_verification_request(email.email)
        res.status_code = status.HTTP_204_NO_CONTENT
    
    @router.post("email-verification/confirm")
    def verify_email(self, token: str, res: Response) -> Any:
        self._get_service().verify_email(token)
        res.status_code = status.HTTP_204_NO_CONTENT
        
        
        
    