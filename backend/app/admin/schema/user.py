from datetime import datetime

from pydantic import ConfigDict, EmailStr, Field, HttpUrl, model_validator
from typing_extensions import Self

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase
from backend.schemas.role import GetRoleListDetails



class UserBase(SchemaBase):
    firstname: str | None = None
    lastname: str | None = None
    fullname: str | None = None
    phone: str | None = None
    pseudo: str | None = None
    email_verified: bool = False
    country_code: str | None = None
    profile_image: dict | None = None
    

class UserLoginSchema(SchemaBase):
    email: EmailStr
    password: str


class UserRegister(SchemaBase):
    password: str
    email: EmailStr


class UserUpdate(UserBase):
    pass


class UserInfoSchemaBase(UserBase):
    email: EmailStr



class GetUserInfoNoRelationDetail(UserInfoSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    x_id: str
    profile_image: dict | None = None
    status: bool
    join_time: datetime = None
    last_login_time: datetime | None = None



class GetUserInfoListDetails(GetUserInfoNoRelationDetail):
    model_config = ConfigDict(from_attributes=True)

    roles: list[GetRoleListDetails] | None = []


class GetCurrentUserInfoDetail(GetUserInfoListDetails):
    model_config = ConfigDict(from_attributes=True)

    roles: list[GetRoleListDetails] | list[str] | None = []

    @model_validator(mode='after')
    def handel(self) -> Self:
        """Dealing with sectors and roles"""
        roles = self.roles
        if roles:
            self.roles = [{'name': role.name} for role in roles]  # type: ignore
        return self


class CurrentUserIns(GetUserInfoListDetails):
    model_config = ConfigDict(from_attributes=True)


class UpdatePasswordParam(SchemaBase):
    old_password: str
    new_password: str
    confirm_password: str
