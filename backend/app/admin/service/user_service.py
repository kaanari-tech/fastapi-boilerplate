import random
from typing import Union

from fastapi import Request
from pydantic import EmailStr
from sqlalchemy import Select, Sequence

from backend.app.admin.service.secure_token_service import secure_token_service
from backend.common.enums import Secure_token_type
from backend.crud.crud_user import user_dao
from backend.models import User
from backend.schemas.user import (
    UpdatePasswordParam,
    UserResetPassword,
    UpdateUserParam
)
from backend.common.exception import errors
from backend.common.security.jwt import get_hash_password, password_verify, superuser_verify
from backend.core.conf import settings
from backend.database.db_postgres import async_db_session
from backend.database.db_redis import redis_client
from backend.common.enums import Role as Role_enum



class ClientService:
    @staticmethod
    async def pwd_update(*, request: Request, obj: UpdatePasswordParam) -> int:
        async with async_db_session.begin() as db:
            user = await user_dao.get(db, request.user.id)
            if not password_verify(f'{obj.old_password}{user.salt}', user.password):
                raise errors.ForbiddenError(msg='Original password is wrong')
            
            np1 = obj.new_password
            np2 = obj.confirm_password

            if np1 != np2:
                raise errors.ForbiddenError(msg='Inconsistent password entry')

            new_pwd = get_hash_password(f'{obj.new_password}{user.salt}')
            count = await user_dao.reset_password(db, request.user.id, new_pwd)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}',
                f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}',
            ]
            for key in key_prefix:
                await redis_client.delete_prefix(key)
            return count
    
    @staticmethod
    async def pwd_reset(*, email: EmailStr, token: str, obj: UserResetPassword) -> int:
        async with async_db_session.begin() as db:
            user = await user_dao.get_by_email(db, email)
            if not user:
                raise errors.NotFoundError(msg='Invalid information')
            np1 = obj.new_password
            np2 = obj.confirm_password

            if np1 != np2:
                raise errors.ForbiddenError(msg='Inconsistent password entry')
            check_token = await secure_token_service.check_token(token=token, user_x_id=user.x_id, type=Secure_token_type.RESET_PWD)
            if not check_token:
                raise errors.ForbiddenError(msg='Token is invalid')
            
            new_pwd = get_hash_password(f'{obj.new_password}{user.salt}')
            count = await user_dao.reset_password(db, user.id, new_pwd)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user.id}',
                f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}',
            ]
            for key in key_prefix:
                await redis_client.delete_prefix(key)
            return count
        
    @staticmethod
    async def get_userinfo(*, email: str) -> User:
        async with async_db_session() as db:
            user = await user_dao.get_with_relation(db, email=email)
            if not user:
                raise errors.NotFoundError(msg='The user does not exist')
            return user
    @staticmethod
    async def get_by_email(*, email: EmailStr) -> User | None:
        async with async_db_session() as db:
            user = await user_dao.get_with_relation(db, email=email)
            return user
    @staticmethod
    async def update_profile_image(*, request: Request, email: str, profile_image: dict) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_by_email(db, email)
            if not input_user:
                raise errors.NotFoundError(msg='The user does not exist')
            count = await user_dao.update_profile_image(db, input_user.id, profile_image)
            return count
    
    @staticmethod
    async def update(*, id: int, obj: UpdateUserParam) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_with_relation(db, id=id, populates=[])
            if not input_user:
                raise errors.NotFoundError(msg='The user does not exist')

            count = await user_dao.update_user_info(db, id, obj.model_dump(exclude_none=True, exclude_unset=True, exclude={}))
            return count
    @staticmethod
    async def get_profile(*, id: int) -> User:
        async with async_db_session() as db:
            user = await user_dao.get_with_relation(db, id=id, populates=[])
            if not user:
                raise errors.NotFoundError(msg='The user does not exist')
            return user

    @staticmethod
    async def get_select(
        *, 
        q: str | None = None, 
        email: str | None = None, 
        phone: str | None = None, 
        status: bool | None = None, 
        role: str | None = None 
    ) -> Select:
        async with async_db_session() as db:
            return await user_dao.get_list(email=email, phone=phone, status=status)

    @staticmethod
    async def get_all() -> Sequence[User]:
        async with async_db_session() as db:
            users = await user_dao.get_all(db)
            return users
    @staticmethod
    async def delete(*, email: str) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_by_email(db, email=email)
            if not input_user:
                raise errors.NotFoundError(msg='The user does not exist')
            count = await user_dao.delete(db, input_user.id)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{input_user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{input_user.id}',
            ]
            for key in key_prefix:
                await redis_client.delete_prefix(key)
            return count

    @staticmethod
    async def get_by_x_id(x_id: str) -> User | None:
        async with async_db_session() as db:
            return await user_dao.get_by_stb_id(db, x_id)

    
user_service = ClientService()
