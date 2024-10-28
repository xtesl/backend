from typing import Any
from enum import Enum

from fastapi import HTTPException


from src.users.models import User, AccountStatus, AccountType


class VER_TYPE(str, Enum):
    EMAIL = "email"
    KYC_EMAIL = "kyc_email" 
    KYC = "kyc"


class Permission:
    def __init__(self, current_user):
        self.current_user: User =  current_user
    
    
    def res_HTTP403(self, message: str):
        raise HTTPException(status_code=400, detail=message)
    
    
    def check_verification(self, type: VER_TYPE) -> None:
        match type:
            case VER_TYPE.EMAIL:
                if not self.current_user.is_verified_email:
                    self.res_HTTP403("User needs to complete email verification")
            case VER_TYPE.KYC:
                if not self.current_user.is_verified_kyc:
                    self.res_HTTP403("Student needs to complete KYC verification")
            case VER_TYPE.KYC_EMAIL:
                email = self.current_user.is_verified_email
                kyc = self.current_user.is_verified_kyc
                if not email and not kyc:
                    self.res_HTTP403("Student needs to complete KYC and email verifications")
                    
    def check_user_type(self, checking_type: AccountType) -> None:
        if self.current_user.account_type is checking_type:
            return True
        return False

        
            
                
        