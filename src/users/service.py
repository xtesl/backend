from datetime import datetime
from typing import Any

from sqlmodel import Session
from fastapi import HTTPException, status

from .models import UserAccount, AccountType, Freelancer, Employer
from .schemas import (
    UserCreate, 
    UserUpdateMe, 
    UpdatePassword, 
    UserPublicWithTypeDetails,
    # UpdateProfile,
    # ProfilePublicEmployer,
    # ProfilePublicFreelancer
)
from src.institutions.models import Institution
from src.utils.db import get_object_or_404, save, get_object_with_pk_or_404
from src.core.security import get_password_hash
from src.authentication.utils import verify_password
# from src.core.permissions import Permission, VER_TYPE
# from src.finance.models import Subscription, SubscriptionPlan, SubscriptionPlanType


class UserService:
    """Service for handling user-related actions and validations"""
    
    def __init__(self, session: Session, current_user: UserAccount | None = None):
        self.current_user = current_user
        self.session = session
    
    # def _get_permission(self) -> Permission:
    #     return Permission(self.current_user)
    
    async def sign_up_user(
        self, 
        user_data: UserCreate, 
        acc_type: AccountType, 
        **kwargs
    ) -> UserAccount:
        """
        Sign up user.This creates a user account and set up a freelancer or an employer
        profile.
        """
        
        # Check account existence
        user = get_object_or_404(self.session, UserAccount.email, user_data.email, False)
        if user:
            raise HTTPException(400, "User with this email address already exists.")
        
        validated_user_account = UserAccount.model_validate(
            user_data,
            update={
                "hashed_password": get_password_hash(user_data.password),
                "type": acc_type
            }
        )
        saved_user_account = save(self.session, validated_user_account, True)
        
        # Minimum freelancer profile setup
        if acc_type is AccountType.FREELANCER:
            institution = get_object_or_404(
                self.session,
                Institution.nick,
                kwargs.get("institution_nick"),
                False
            ) 
            if not institution:
                raise HTTPException(
                    400,
                    "institution_nick specified is not associated with any institution."
                )
            
            profile = Freelancer(
                 user_account_pk=saved_user_account.pk,
                 university=institution
            )
        
        # Employer profile setup
        elif acc_type is AccountType.EMPLOYER:
            profile = Employer(
                user_account_pk=saved_user_account.pk
            )
            
        save(self.session, profile, True)
        return saved_user_account
    
    # async def update_user_account(self, user_data: UserUpdateMe, partial: bool = True) -> User:
    #     """
    #     Update basic user info i.e email, username and full_name.
    #     """
    #     if user_data.email:
    #         existing_user = get_object_or_404(
    #             self.session,
    #             User.email,
    #             user_data.email,
    #             False
    #         )
    #         if existing_user:
    #             raise HTTPException(409, "User with this email already exists.")
        
    #     user_data = user_data.model_dump(exclude_unset=partial) 
    #     self.current_user.sqlmodel_update(user_data)
    #     return save(self.session, self.current_user, refresh=True)
    
    def update_password(self, data: UpdatePassword) -> None:
        """
        Update user's password. NOTE: This is different from password resetting,
        this can only be done after authorization.
        """
        if not verify_password(data.current_password, self.current_user.hashed_password):
            raise HTTPException(400, "Incorrect password")
        
        self.current_user.hashed_password = get_password_hash(data.new_password)
        save(self.session, self.current_user)
    
    # def update_profile(self, data: UpdateProfile, partial: bool = True) -> Profile:
    #     """
    #     Users need to complete emaill verification before they can update their profiles.
    #     """
    #     self._get_permission().check_verification(type=VER_TYPE.EMAIL)
        
    #     employer_fields = {"location", "company_website", "company_name", "name"}
    #     freelancer_fields = {"program"}
        
    #     # Run update according to account type
    #     if self.current_user.account_type is AccountType.EMPLOYER:
    #         user_data = data.model_dump(exclude_unset=partial, exclude=freelancer_fields)
    #     else:
    #         user_data = data.model_dump(exclude_unset=partial, exclude=employer_fields)
        
    #     self.current_user.sqlmodel_update(user_data)
    #     save(self.session, self.current_user)
        
    #     response_data = (
    #      ProfilePublicEmployer(**user_data)
    #      if self.current_user.account_type is AccountType.EMPLOYER
    #      else ProfilePublicFreelancer(**user_data)
    #   )
    #     return response_data
    
    
    def get_user(self, type_details: bool) -> UserAccount:
         """
         Retrieve user's account details.It may include user's account type details.
         """
         # Admins are associated with only basic account details.
         if self.current_user.type is AccountType.ADMIN:
             return self.current_user
         
        # Retrieve user without account type details
         if not type_details:
             return self.current_user
         
         # Customer account types
         customer_account_types = {
             AccountType.FREELANCER: Freelancer,
             AccountType.EMPLOYER: Employer
         }
         
         account_type = customer_account_types[self.current_user.type]
         
         # Account type details
         account_type_details = get_object_or_404(
               self.session,
               account_type.user_account_pk,
               self.current_user.pk,
         )
         
         user_account_data = self.current_user.model_dump() 
         
         match self.current_user.type:
             case AccountType.EMPLOYER:
                    return UserPublicWithTypeDetails(
                        **user_account_data, 
                        type_details=account_type_details
                     )
                    
             case AccountType.FREELANCER: 
                    return UserPublicWithTypeDetails(
                         **user_account_data,
                         type_details=account_type_details
                     )
         
        
        
        
            
            
            
            
        