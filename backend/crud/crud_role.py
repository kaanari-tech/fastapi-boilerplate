from sqlalchemy import Sequence, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from backend.crud.crud_base import CRUDBase

from backend.models import Role, Role
from backend.app.admin.schema.role import (
    CreateRoleParam,
    UpdateRoleParam,
)
from backend.models.user import User


class CRUDRole(CRUDBase[Role]):
    async def get(self, db: AsyncSession, role_id: int) -> Role | None:
        """
        Getting Roles

        :param db:
        :param role_id:
        :return:
        """
        return await self.select_model(db, role_id)

    async def get(self, db, role_id: int) -> Role | None:
        """
        Get role by id

        :param db:
        :param role_id:
        :return:
        """
        return await self.select_model(db, role_id)

    async def get_all(self, db) -> Sequence[Role]:
        """
        Get all roles

        :param db:
        :return:
        """
        return await self.select_models(db)

    async def get_user_roles(self, db, user_id: int) -> Sequence[Role]:
        """
        Get user roles

        :param db:
        :param user_id:
        :return:
        """
        stmt = select(self.model).join(self.model.users).where(User.id == user_id)
        roles = await db.execute(stmt)
        return roles.scalars().all()

    async def get_list(
        self, name: str = None, data_scope: int = None, status: int = None
    ) -> Select:
        """
        Get role list

        :param name:
        :param data_scope:
        :param status:
        :return:
        """
        stmt = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if name:
            where_list.append(self.model.name.like(f"%{name}%"))
        if data_scope:
            where_list.append(self.model.data_scope == data_scope)
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(*where_list)
        return stmt

    async def get_by_name(self, db, name: str) -> Role | None:
        """
        Get role by name

        :param db:
        :param name:
        :return:
        """
        roles =  await self.select_model_by_column(db, name=name)

        return roles

    async def create(self, db, obj_in: CreateRoleParam) -> None:
        """
        Creating roles

        :param db:
        :param obj_in:
        :return:
        """
        await self.create_model(db, obj_in)

    async def update(self, db, role_id: int, obj_in: UpdateRoleParam) -> int:
        """
        Updating roles

        :param db:
        :param role_id:
        :param obj_in:
        :return:
        """
        return await self.update_model(db, role_id, obj_in)

    async def delete(self, db, role_id: list[int]) -> int:
        """
        Delete roles

        :param db:
        :param role_id:
        :return:
        """
        return await self.delete_model_by_column(
            db, allow_multiple=True, id__in=role_id
        )


role_dao: CRUDRole = CRUDRole(Role)
