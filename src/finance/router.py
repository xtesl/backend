from typing import Any


from fastapi_utils.cbv import cbv
from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.api.deps import get_db, CurrentUser, CurrentEmployerUser
from .service import FinanceService
from src.users.models import User

router = APIRouter()

@cbv(router)
class FinanceRouter:
    session: Session = Depends(get_db)
    
    
    def _get_service(self, current_user: User | None) -> FinanceService:
        return FinanceService(self.session, current_user)
    
    
    @router.get("/financial-account")
    def get_financial_account(self, current_user: CurrentUser) -> Any:
        return self._get_service(current_user).get_financial_account()
    
    @router.post("/deposit")
    def deposit_amount(self, current_user: CurrentEmployerUser) -> Any:
        pass

