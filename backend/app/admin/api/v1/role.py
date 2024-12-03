from typing import Annotated
from fastapi import APIRouter, Path, Query, Request
from backend.common.pagination import DependsPagination, paging_data
from backend.database.db_postgres import CurrentSession
from backend.utils.serializers import select_as_dict, select_list_serialize

from backend.schemas.role import GetRoleListDetails, UpdateRoleParam, CreateRoleParam
from backend.app.admin.service.role_service import role_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth

router = APIRouter(prefix="/role", tags=["Role"])


@router.get("/all", summary="Get all roles", dependencies=[DependsJwtAuth])
async def get_all_roles(request: Request,) -> ResponseModel:
    roles = await role_service.get_all()
    data = select_list_serialize(roles)
    return response_base.success(request=request, data=data)


@router.get("/{pk}/all", summary="Get all user roles", dependencies=[DependsJwtAuth])
async def get_user_all_roles(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    roles = await role_service.get_user_roles(pk=pk)
    data = select_list_serialize(roles)
    return response_base.success(request=request, data=data)


@router.get(
    "/{pk}",
    summary="Get role by ID",
    dependencies=[DependsJwtAuth]
)
async def get_role(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    role = await role_service.get_by_id(role_id=pk)
    data = GetRoleListDetails(**select_as_dict(role))
    return response_base.success(request=request, data=data)


@router.get(
    "/",
    summary="Get roles pagination",
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_roles(
    request: Request,
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    data_scope: Annotated[int | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseModel:
    role_select = await role_service.get_select(
        name=name, data_scope=data_scope, status=status
    )
    page_data = await paging_data(db, role_select, GetRoleListDetails)
    return response_base.success(request=request, data=page_data)


@router.post(
    "/",
    summary="Role creation",
    dependencies=[
        #     Depends(RequestPermission('sys:role:add')),
        #     DependsRBAC,
        DependsJwtAuth,
    ],
)
async def create_role(request: Request, obj: CreateRoleParam) -> ResponseModel:
    await role_service.create(obj=obj)
    return response_base.success(request=request)


@router.put(
    "/{pk}",
    summary="Update role",
    dependencies=[
        #     Depends(RequestPermission('sys:role:edit')),
        #     DependsRBAC,
        DependsJwtAuth,
    ],
)
async def update_role(
    request: Request,
    pk: Annotated[int, Path(...)], obj: UpdateRoleParam
) -> ResponseModel:
    count = await role_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success(request=request)
    return response_base.fail(request=request)


@router.delete(
    "/",
    summary="Delete roles",
    dependencies=[
        #     Depends(RequestPermission('sys:role:del')),
        #     DependsRBAC,
        DependsJwtAuth,
    ],
)
async def delete_role(request: Request, pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await role_service.delete(pk=pk)
    if count > 0:
        return response_base.success(request=request)
    return response_base.fail(request=request)
