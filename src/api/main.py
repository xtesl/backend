from fastapi import APIRouter

from src.users.router import router as user_router
from src.authentication.router import router as auth_router


api_router = APIRouter()

api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
# api_router.include_router(institution.router, prefix="/institution", tags=["inst"])
# api_router.include_router(job.router, prefix="/job", tags=["job"])