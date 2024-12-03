from typing import Annotated

from fastapi import APIRouter, Query, Request

from backend.app.admin.schema.opera_log import GetOperaLogListDetails
from backend.app.admin.service.opera_log_service import opera_log_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.rbac import DependsRBAC
from backend.database.db_postgres import CurrentSession

router = APIRouter(prefix="/opera_log", tags=["Operation Log"])


@router.get(
    '/',
    summary='(Fuzzy Condition) Paging for Operation Logs',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_opera_logs(
    request: Request,
    db: CurrentSession,
    username: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
    ip: Annotated[str | None, Query()] = None,
) -> ResponseModel:
    log_select = await opera_log_service.get_select(username=username, status=status, ip=ip)
    page_data = await paging_data(db, log_select, GetOperaLogListDetails)
    return response_base.success(request=request, data=page_data)


@router.delete(
    '/',
    summary='Delete (batch) operation logs',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_opera_log(request: Request, pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await opera_log_service.delete(pk=pk)
    if count > 0:
        return response_base.success(request=request)
    return response_base.fail(request=request)


@router.delete(
    '/all',
    summary='Delete (batch) operation log',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_all_opera_logs(request: Request) -> ResponseModel:
    count = await opera_log_service.delete_all()
    if count > 0:
        return response_base.success(request=request)
    return response_base.fail(request=request)
