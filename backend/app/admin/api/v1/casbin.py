from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request

from backend.app.admin.schema.casbin_rule import (
    CreatePolicyParam,
    CreateUserRoleParam,
    DeleteAllPoliciesParam,
    DeletePolicyParam,
    DeleteUserRoleParam,
    GetPolicyListDetails,
    UpdatePolicyParam,
)
from backend.app.admin.service.casbin_service import casbin_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.rbac import DependsRBAC
from backend.database.db_postgres import CurrentSession

router = APIRouter(prefix='/casbin', tags=["Casbin"])


@router.get(
    '/',
    summary='(Fuzzy condition) Get all permission policies with pagination',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_casbin(
    request: Request,
    db: CurrentSession,
    ptype: Annotated[str | None, Query(description='Policy type, p / g')] = None,
    sub: Annotated[str | None, Query(description='User UUID / Role')] = None,
) :
    casbin_select = await casbin_service.get_casbin_list(ptype=ptype, sub=sub)
    page_data = await paging_data(db, casbin_select, GetPolicyListDetails)
    return response_base.success(request=request, data=page_data)

@router.get('/policies', summary='Get all P permission policies', dependencies=[DependsJwtAuth])
async def get_all_policies(request: Request, role: Annotated[int | None, Query(description='Role ID')] = None) -> ResponseModel:
    policies = await casbin_service.get_policy_list(role=role)
    return response_base.success(request=request, data=policies)


@router.post(
    '/policy',
    summary='Add P permission policy',
    dependencies=[
        DependsRBAC,
    ],
)
async def create_policy(request: Request, p: CreatePolicyParam) -> ResponseModel:
    """
    P Policy:

    - It is recommended to add role-based access control, which needs to be combined with adding G policies to actually have access rights. Suitable for configuring global interface access policies.<br>
    **Format**: Role + Access Path + Access Method

    - If adding user-based access control, there is no need to add G policies to actually have access rights. Suitable for configuring specific user interface access policies.<br>
    **Format**: User UUID + Access Path + Access Method
    """
    data = await casbin_service.create_policy(p=p)
    return response_base.success(request=request, data=data)


@router.post(
    '/policies',
    summary='Add multiple P permission policies',
    dependencies=[
        DependsRBAC,
    ],
)
async def create_policies(request: Request, ps: list[CreatePolicyParam]) -> ResponseModel:
    data = await casbin_service.create_policies(ps=ps)
    return response_base.success(request=request, data=data)


@router.put(
    '/policy',
    summary='Update P permission policy',
    dependencies=[
        DependsRBAC,
    ],
)
async def update_policy(request: Request, old: UpdatePolicyParam, new: UpdatePolicyParam) -> ResponseModel:
    data = await casbin_service.update_policy(old=old, new=new)
    return response_base.success(request=request, data=data)


@router.put(
    '/policies',
    summary='Update multiple P permission policies',
    dependencies=[
        DependsRBAC,
    ],
)
async def update_policies(request: Request, old: list[UpdatePolicyParam], new: list[UpdatePolicyParam]) -> ResponseModel:
    data = await casbin_service.update_policies(old=old, new=new)
    return response_base.success(request=request, data=data)


@router.delete(
    '/policy',
    summary='Delete P permission policy',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_policy(request: Request, p: DeletePolicyParam) -> ResponseModel:
    data = await casbin_service.delete_policy(p=p)
    return response_base.success(request=request, data=data)


@router.delete(
    '/policies',
    summary='Delete multiple P permission policies',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_policies(request: Request, ps: list[DeletePolicyParam]) -> ResponseModel:
    data = await casbin_service.delete_policies(ps=ps)
    return response_base.success(request=request, data=data)


@router.delete(
    '/policies/all',
    summary='Delete all P permission policies',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_all_policies(request: Request, sub: DeleteAllPoliciesParam) -> ResponseModel:
    count = await casbin_service.delete_all_policies(sub=sub)
    if count > 0:
        return response_base.success(request=request )
    return response_base.fail(request=request)


@router.get('/groups', summary='Get all G permission policies', dependencies=[DependsJwtAuth])
async def get_all_groups(request: Request) -> ResponseModel:
    data = await casbin_service.get_group_list()
    return response_base.success(request=request, data=data)


@router.post(
    '/group',
    summary='Add G permission policy',
    dependencies=[
        DependsRBAC,
    ],
)
async def create_group(request: Request, g: CreateUserRoleParam) -> ResponseModel:
    """
    G Policy (**Depends on P policy**):

    - If you add role-based access control in the P policy, you also need to add group-based access control in the G policy to actually have access rights.<br>
    **Format**: User UUID + Role

    - If you add user-based access control in the P policy, there is no need to add the corresponding G policy to have access rights.<br>
    However, you will not have all the permissions of the user role, but only the specific access rights added by the corresponding P policy.
    """
    data = await casbin_service.create_group(g=g)
    return response_base.success(request=request, data=data)


@router.post(
    '/groups',
    summary='Add multiple G permission policies',
    dependencies=[
        DependsRBAC,
    ],
)
async def create_groups(request: Request, gs: list[CreateUserRoleParam]) -> ResponseModel:
    data = await casbin_service.create_groups(gs=gs)
    return response_base.success(request=request, data=data)


@router.delete(
    '/group',
    summary='Delete G permission policy',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_group(request: Request, g: DeleteUserRoleParam) -> ResponseModel:
    data = await casbin_service.delete_group(g=g)
    return response_base.success(request=request, data=data)


@router.delete(
    '/groups',
    summary='Delete multiple G permission policies',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_groups(request: Request, gs: list[DeleteUserRoleParam]) -> ResponseModel:
    data = await casbin_service.delete_groups(gs=gs)
    return response_base.success(request=request, data=data)


@router.delete(
    '/groups/all',
    summary='Delete all G permission policies',
    dependencies=[
        DependsRBAC,
    ],
)
async def delete_all_groups(request: Request, uuid: Annotated[UUID, Query(...)]) -> ResponseModel:
    count = await casbin_service.delete_all_groups(uuid=uuid)
    if count > 0:
        return response_base.success(request=request)
    return response_base.fail(request=request)
