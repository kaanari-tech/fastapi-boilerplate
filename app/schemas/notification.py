from datetime import datetime
from enum import Enum

from fastapi import Query

from app.schemas import UserResponse
from app.schemas.core import BaseSchema
from app.schemas.core import PagingMeta
from app.schemas.core import SortQueryIn


class NotificationBase(BaseSchema):
    content: str
    viewed: bool
    type: str


class NotificationCreate(NotificationBase):
    user_id: str


# Properties to receive via API on update
class NotificationUpdate(BaseSchema):
    content: str | None
    viewed: bool | None
    type: str | None
    pass


class NotificationResponse(NotificationBase):
    user: UserResponse | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationsPagedResponse(BaseSchema):
    data: list[NotificationResponse] | None
    meta: PagingMeta | None


class NotificationSortFieldEnum(Enum):
    created_at = "created_at"


class NotificationSortQueryIn(SortQueryIn):
    sort_field: NotificationSortFieldEnum | None = Query(
        NotificationSortFieldEnum.created_at
    )
