from fastapi import APIRouter

from app.api.v1.endpoints import health, homework, speaking

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(homework.router, prefix="/homework", tags=["homework"])
api_router.include_router(speaking.router, prefix="/speaking", tags=["speaking"])
