

from fastapi_utils.cbv import cbv
from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.api.deps import CurrentEmployerUser, get_employer
from .schemas import JobCreate, JobPublic
from .service import JobService
from src.users.models import User

router = APIRouter()

@cbv(router)
class JobRouter:
    session: Session = Depends(get_employer)
    
    def _get_service(self, current_user: User) -> JobService:
        return JobService(self.session, current_user)
        
    
    @router.post("/")
    async def create_job(self, current_user: CurrentEmployerUser, body: JobCreate) -> JobPublic:
        await self._get_service(current_user).create_job(data=body)
    
    
        