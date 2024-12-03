from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.crud.crud_base import CRUDBase

from backend.models import CasbinRule
from backend.app.admin.schema.casbin_rule import DeleteAllPoliciesParam


class CRUDCasbin(CRUDBase[CasbinRule]):
    async def get_list(self, ptype: str, sub: str) -> Select:
        """
        Getting a list of casbin policies

        :param ptype:
        :param sub:
        :return:
        """
        return await self.select_order('id', 'desc', ptype=ptype, v0__like=f'%{sub}%')

    async def delete_policies_by_sub(self, db: AsyncSession, sub: DeleteAllPoliciesParam) -> int:
        """
        Delete all P casbin policies for the role

        :param db:
        :param sub:
        :return:
        """
        where_list = [sub.role]
        if sub.uuid:
            where_list.append(sub.uuid)
        return await self.delete_model_by_column(db, allow_multiple=True, v0__mor={'eq': where_list})

    async def delete_groups_by_uuid(self, db: AsyncSession, uuid: UUID) -> int:
        """
        Delete all G casbin policies for a user

        :param db:
        :param uuid:
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, v0=str(uuid))


casbin_dao: CRUDCasbin = CRUDCasbin(CasbinRule)
