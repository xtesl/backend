from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.main import api_router
from src.core.db import init_db
from src.core.config import settings

app = FastAPI(debug=True)

# Create database tables
# init_db()
# Set all CORS enabled origins

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
  
app.include_router(api_router)
