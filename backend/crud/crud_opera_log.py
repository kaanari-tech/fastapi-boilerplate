from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.crud.crud_base import CRUDBase

from backend.models import OperaLog
from backend.app.admin.schema.opera_log import CreateOperaLogParam


class CRUDOperaLogDao(CRUDBase[OperaLog]):
    async def get_list(self, username: str | None = None, status: int | None = None, ip: str | None = None) -> Select:
        """
        Getting a list of operation logs

        :param username:
        :param status:
        :param ip:
        :return:
        """
        filters = {}
        if username is not None:
            filters.update(username=f'%{username}%')
        if status is not None:
            filters.update(status=status)
        if ip is not None:
            filters.update(ip=f'%{ip}%')
        return await self.select_order('created_time', 'desc', **filters)

    async def create(self, db: AsyncSession, obj_in: CreateOperaLogParam) -> None:
        """
        Creating operation logs

        :param db:
        :param obj_in:
        :return:
        """
        await self.create_model(db, obj_in)

    async def delete(self, db: AsyncSession, pk: list[int]) -> int:
        """
        Delete operation log

        :param db:
        :param pk:
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pk)

    async def delete_all(self, db: AsyncSession) -> int:
        """
        Delete all operation logs

        :param db:
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True)


opera_log_dao: CRUDOperaLogDao = CRUDOperaLogDao(OperaLog)