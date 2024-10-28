from typing import Annotated, Any, Union

from fastapi import APIRouter, Query, Depends, Response, status
from fastapi_utils.cbv import cbv
from sqlmodel import Session


from .service import UserService
from .schemas import (
    UserCreate, 
    UserPublic, 
    UserUpdateMe, 
    UpdatePassword,
    UserPublicWithTypeDetails
    # UserPublicWithProfile,
    # UpdateProfile,
    # ProfilePublicEmployer,
    # ProfilePublicFreelancer,
    # ProfilePublic
)

from .models import AccountType, UserAccount
from src.api.deps import CurrentUser, get_db, NormalUser
# from src.core.permissions import access_control


router = APIRouter()

@cbv(router)
class UserRouter:
    session: Session = Depends(get_db)
    
    def _get_user_service(self, current_user: UserAccount | None = None) -> UserService:
        return UserService(self.session, current_user)
    
    @router.get("/me", response_model=Union[UserPublic, UserPublicWithTypeDetails])
    def get_user(
        self,
        current_user: CurrentUser,
        type_details: Annotated[bool, Query(
        description="Profile info is returned alongside basic user info when enabled."
    )] = False,
   ) -> Any:
        return self._get_user_service(current_user).get_user(type_details)
    
#     @router.patch("/me/profile")
#     def update_profile(self, current_user: NormalUser, body: UpdateProfile) -> Any:
#         return self._get_user_service(current_user).update_profile(body, partial=True)
    
#     @router.get("/me/profile", response_model=Union[
#         ProfilePublicEmployer, 
#         ProfilePublicFreelancer
#         ])
#     def get_profile(self, current_user: NormalUser) -> Any:
#         return current_user.profile
    
    @router.patch("me/password")
    def update_password(
        self,
        current_user: CurrentUser,
        body: UpdatePassword,
        res: Response
    ) -> Any:
        self._get_user_service(current_user).update_password(data=body)
        res.status_code = status.HTTP_204_NO_CONTENT
        
    @router.post(
    "/{account_type}",
    response_model=UserPublic
  )
    async def sign_up(
    self,
    account_type: AccountType,
    user_in: UserCreate,
    institution_nick: Annotated[str, Query(
        description="University's nickname.Required for freelancer accounts"
    )] = None
   ) -> Any:
        service = self._get_user_service()
        return await service.sign_up_user(
            user_data=user_in,
            acc_type=account_type,
            institution_nick=institution_nick
        )
        
    # @router.patch("/me", response_model=UserPublic)
    # async def update_user_account(self, current_user: CurrentUser, user_in: UserUpdateMe) -> Any:
    #     service = self._get_user_service(current_user)
    #     return await service.update_user_account(user_data=user_in, partial=True)
    
   
        