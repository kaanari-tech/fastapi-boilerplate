from datetime import datetime
from enum import Enum

from fastapi import Query
from pydantic import EmailStr

from app.schemas.core import BaseSchema
from app.schemas.core import PagingMeta
from app.schemas.core import SortQueryIn


class UserBase(BaseSchema):
    firstname: str
    lastname: str
    phone: str


class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(BaseSchema):
    password: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    phone: str | None = None


class UserResponse(UserBase):
    id: str
    email: EmailStr
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsersPagedResponse(BaseSchema):
    data: list[UserResponse] | None
    meta: PagingMeta | None


class UserSortFieldEnum(Enum):
    created_at = "created_at"
    title = "title"


class UserSortQueryIn(SortQueryIn):
    sort_field: UserSortFieldEnum | None = Query(UserSortFieldEnum.created_at)
