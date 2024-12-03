from typing import Annotated, Union
from fastapi import APIRouter, Path, Query, Request
from backend.common.enums import Role
from backend.common.pagination import DependsPagination, paging_data
from backend.database.db_postgres import CurrentSession
from backend.utils.serializers import select_as_dict

from backend.app.admin.schema.user import GetUserInfoListDetails, UserUpdate
from backend.app.admin.service.user_service import user_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth

router = APIRouter(prefix="/user", tags=["User"])



# @router.get(
#     "/{pk}",
#     summary="Get user by ID",
# )
# async def get_user(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
#     user = await user_service.get_by_id(user_id=pk)
#     data = GetUserInfoListDetails(**select_as_dict(user))
#     return response_base.success(request=request, data=data)


@router.get(
    "/",
    summary="Get users pagination",
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_users(
    request: Request,
    db: CurrentSession,
    query: Annotated[str | None, Query()] = None,
    role: Annotated[Union[Role, str] | None, Query()] = None,
    status: Annotated[bool | None, Query()] = None,
) -> ResponseModel:
    user_select = await user_service.get_select(
        q=query, role=role, status=status
    )
    page_data = await paging_data(db, user_select, GetUserInfoListDetails)
    return response_base.success(request=request, data=page_data)

