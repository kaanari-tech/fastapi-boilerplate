from datetime import datetime

from fastapi import Request
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.crud_login_log import login_log_dao
from backend.app.admin.schema.login_log import CreateLoginLogParam
from backend.common.log import log
from backend.database.db_postgres import async_db_session


class LoginLogService:
    @staticmethod
    async def get_select(*, username: str, status: int, ip: str) -> Select:
        return await login_log_dao.get_list(username=username, status=status, ip=ip)

    @staticmethod
    async def create(
        *,
        db: AsyncSession,
        request: Request,
        user_x_id: str,
        email: str,
        login_time: datetime,
        status: int,
        msg: str,
    ) -> None:
        try:
            obj_in = CreateLoginLogParam(
                user_x_id=user_x_id,
                email=email,
                status=status,
                ip=request.state.ip,
                country=request.state.country,
                region=request.state.region,
                city=request.state.city,
                user_agent=request.state.user_agent,
                browser=request.state.browser,
                os=request.state.os,
                device=request.state.device,
                msg=msg,
                login_time=login_time,
            )
            await login_log_dao.create(db, obj_in)
        except Exception as e:
            log.error(f'Login log creation failure: {e}')

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await login_log_dao.delete(db, pk)
            return count

    @staticmethod
    async def delete_all() -> int:
        async with async_db_session.begin() as db:
            count = await login_log_dao.delete_all(db)
            return count


login_log_service = LoginLogService()
