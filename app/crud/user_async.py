from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from .crud_async_base import CRUDAsyncBase
from app import models
from app import schemas
from app.core.security import verify_password


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

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> models.User | None:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user


user = CRUDUserAsync(
    models.User,
    response_schema_class=schemas.UserResponse,
    list_response_class=schemas.UsersPagedResponse,
)
