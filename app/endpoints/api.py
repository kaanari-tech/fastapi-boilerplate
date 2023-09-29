from fastapi import APIRouter

from app.endpoints.v1 import user

v1_router = APIRouter()

v1_router.include_router(user.router, prefix="/user", tags=["User"])
