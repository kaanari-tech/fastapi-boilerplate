from .user_async import user
from app import models
from app import schemas
from app.crud.crud_sync_base import CRUDSyncBase

user_sync: CRUDSyncBase[
    models.User,
    schemas.UserCreate,
    schemas.UserUpdate,
    schemas.UserResponse,
    schemas.UsersPagedResponse,
] = CRUDSyncBase(
    model=models.User,
    response_schema_class=schemas.UserResponse,
    list_response_class=schemas.UsersPagedResponse,
)
