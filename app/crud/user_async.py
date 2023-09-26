from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from .crud_async_base import CRUDAsyncBase
from app import models
from app import schemas


class CRUDUserAsync(
    CRUDAsyncBase[
        models.User,
        schemas.UserResponse,
        schemas.UserCreate,
        schemas.UserUpdate,
        schemas.UsersPagedResponse,
    ]
):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> models.User | None:
        stmt = select(models.User).where(models.User.email == email)
        return (await db.execute(stmt)).scalars().first()


user = CRUDUserAsync(
    models.User,
    response_schema_class=schemas.UserResponse,
    list_response_class=schemas.UsersPagedResponse,
)
