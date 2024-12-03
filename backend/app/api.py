from fastapi import APIRouter
from backend.app import Handlers
from backend.core.conf import settings

admin_router = APIRouter(prefix=f"{settings.FASTAPI_API_V1_PATH}")


for handler in Handlers.iterator():
    if getattr(handler, 'router', None):
        if handler.__name__.split('.')[-4] == 'admin':
            admin_router.include_router(handler.router)
