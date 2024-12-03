from typing import Sequence

from fastapi import Request
from sqlalchemy import Select

from backend.crud.crud_role import role_dao
from backend.models import Role
from backend.app.admin.schema.role import CreateRoleParam, UpdateRoleMenuParam, UpdateRoleParam
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.db_postgres import async_db_session
from backend.database.db_redis import redis_client


class RoleService:
    
    @staticmethod
    async def get_by_id(role_id: int) -> Role | None:
        """
        Get role by id

        :param db:
        :param role_id:
        :return:
        """
        async with async_db_session() as db:
            return await role_dao.get(db, role_id)

    @staticmethod
    async def get_all() -> Sequence[Role]:
        async with async_db_session() as db:
            roles = await role_dao.get_all(db)
            return roles

    @staticmethod
    async def get_user_roles(*, pk: int) -> Sequence[Role]:
        async with async_db_session() as db:
            roles = await role_dao.get_user_roles(db, user_id=pk)
            return roles

    @staticmethod
    async def get_select(*, name: str = None, data_scope: int = None, status: int = None) -> Select:
        return await role_dao.get_list(name=name, data_scope=data_scope, status=status)

    @staticmethod
    async def create(*, obj: CreateRoleParam) -> None:
        async with async_db_session.begin() as db:
            role = await role_dao.get_by_name(db, obj.name)
            if role:
                raise errors.ForbiddenError(msg='already exists')
            await role_dao.create(db, obj)

    @staticmethod
    async def get_by_name(name: str) -> Role | None:
        async with async_db_session() as db:
            return await role_dao.get_by_name(db, name)
        
    @staticmethod
    async def update(*, pk: int, obj: UpdateRoleParam) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk)
            if not role:
                raise errors.NotFoundError(msg='not found')
            if role.name != obj.name:
                role = await role_dao.get_by_name(db, obj.name)
                if role:
                    raise errors.ForbiddenError(msg='already exists')
            count = await role_dao.update_roleinfo(db, pk, obj)
            return count

    
    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await role_dao.delete(db, pk)
            return count


role_service = RoleService()