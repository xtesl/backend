
from sqlmodel import Session
from fastapi import HTTPException

from src.users.models import User, AccountType
from src.core.permissions import Permission, VER_TYPE
from src.finance.models import FinancialDetails
from src.utils.db import get_object_with_pk_or_404




class FinanceService:
    def __init__(self, session: Session, current_user: User | None):
        self.session = session
        self.current_user = current_user
    
    
    def _get_permission(self) -> Permission:
        return Permission(self.current_user)
    
    
    def get_financial_account(self, user_pk: str | None = None) -> FinancialDetails:
        """
        Retrieves users' financial details.
        `user_pk` is required when `.current_user` is an admin.
        """
        # Check for email-verified users
        permission = self._get_permission()
        permission.check_verification(VER_TYPE.EMAIL)
        # Admin retrievals
        is_admin = permission.check_user_type(checking_type=AccountType.ADMIN)
        if is_admin:
            return get_object_with_pk_or_404(user_pk, self.session, FinancialDetails)
        # Employers and Freelancers retrievals
        else:
            return get_object_with_pk_or_404(self.current_user.pk, self.session, FinancialDetails)
    
    def make_deposit(self) -> None:
        """ Make a deposit into the payment gateway account"""
        pass
        
        