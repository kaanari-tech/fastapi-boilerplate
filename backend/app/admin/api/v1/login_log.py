from typing import Annotated

from fastapi import APIRouter, Query, Request

from backend.app.admin.schema.login_log import GetLoginLogListDetails
from backend.app.admin.service.login_log_service import login_log_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.rbac import DependsRBAC
from backend.database.db_postgres import CurrentSession

router = APIRouter(prefix="/login_log", tags=["Login log"] )


@router.get(
    '/',
    summary='(Fuzzy Criteria) Paging for Login Logs',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_login_logs(
    request: Request,
    db: CurrentSession,
    username: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
    ip: Annotated[str | None, Query()] = None,
) -> ResponseModel:
    log_select = await login_log_service.get_select(username=username, status=status, ip=ip)
    page_data = await paging_data(db, log_select, GetLoginLogListDetails)
    return response_base.success(request=request, data=page_data)


@router.delete(
    '/',
    summary='(Batch) Delete Login Logs',
    dependencies=[
        DependsRBAC,
        DependsJwtAuth,
        
    ],
)
async def delete_login_log(request: Request, pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await login_log_service.delete(pk=pk)
    if count > 0:
        return response_base.success(request=request)
    return response_base.fail(request=request)


@router.delete(
    '/all',
    summary='Empty login log',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_all_login_logs(request: Request) -> ResponseModel:
    count = await login_log_service.delete_all()
    if count > 0:
        return response_base.success(request=request)
    return response_base.fail(request=request)
