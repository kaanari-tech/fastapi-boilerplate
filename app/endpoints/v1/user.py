from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app import schemas
from app.core.security import get_password_hash
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


@router.get(
    "/{id}",
    operation_id="get_user_by_id",
)
async def get_user_by_id(
    id: str,
    db: AsyncSession = Depends(get_async_db),
) -> schemas.UserResponse:
    user = await crud.user.get_db_obj_by_id(db, id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("/", operation_id="create_user")
async def create_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_async_db),
) -> schemas.UserResponse:
    existing_user = await crud.user.get_by_email(db=db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user_in.email} alrheady exist",
        )
    user_in.password = get_password_hash(user_in.password)
    user = await crud.user.create(db=db, create_schema=user_in)
    return user


@router.put(
    "/{id}",
    operation_id="update_user",
)
async def update_user(
    id: str,
    user_in: schemas.UserUpdate,
    db: AsyncSession = Depends(get_async_db),
) -> schemas.UserResponse:
    user = await crud.user.get_db_obj_by_id(db, id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await crud.user.update(db, db_obj=user, update_schema=user_in)
