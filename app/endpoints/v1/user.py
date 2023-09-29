from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app import schemas
from app.db import get_async_db


router = APIRouter()


@router.get("/", operation_id="get_all_users")
async def get_all_users(
    q: str | None = None,
    paging_query_in: schemas.PagingQueryIn = Depends(),
    sort_query_in: schemas.UserSortQueryIn = Depends(),
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_async_db),
) -> schemas.UsersPagedResponse:
    users = await crud.user.get_paged_list(db=db, paging_query_in=paging_query_in)
    return users
