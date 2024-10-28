from fastapi import FastAPI

from src.api.main import api_router
from src.core.db import init_db
# from app.core.config import settings

app = FastAPI(debug=True)

# Create database tables
# init_db()

app.include_router(api_router)