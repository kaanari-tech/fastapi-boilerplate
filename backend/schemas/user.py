from datetime import datetime

from pydantic import ConfigDict, EmailStr, Field, HttpUrl, model_validator
from typing_extensions import Self

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase
from backend.schemas.role import GetRoleListDetails


class AuthSchemaBase(SchemaBase):
    email: str
    password: str | None


class AuthLoginParam(AuthSchemaBase):
    captcha: str


class RegisterUserParam(AuthSchemaBase):
    email: EmailStr = Field(..., examples=['user@example.com'])


class AddUserParam(AuthSchemaBase):
    roles: list[GetRoleListDetails]
    pseudo: str | None = None
    email: EmailStr = Field(..., examples=['user@example.com'])


class UserInfoSchemaBase(SchemaBase):
    firstname: str | None
    lastname: str | None
    email: EmailStr = Field(..., examples=['user@example.com'])
    phone: str | None = None


class UpdateUserParam(UserInfoSchemaBase):
    pass


class UpdateUserRoleParam(SchemaBase):
    roles: list[int]

class UserResetPassword(SchemaBase):
    new_password: str
    confirm_password: str

class UpdatePasswordParam(SchemaBase):
    old_password: str
    new_password: str
    confirm_password: str

class AvatarParam(SchemaBase):
    url: HttpUrl = Field(..., description='Avatar http address')


class GetUserInfoNoRelationDetail(UserInfoSchemaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    x_id: str
    avatar: str | None = None
    status: StatusType = Field(default=StatusType.enable)
    join_time: datetime = None
    last_login_time: datetime | None = None


class GetUserInfoListDetails(GetUserInfoNoRelationDetail):
    model_config = ConfigDict(from_attributes=True)

    # dept: GetDeptListDetails | None = None
    roles: list[GetRoleListDetails]


class GetCurrentUserInfoDetail(GetUserInfoListDetails):
    model_config = ConfigDict(from_attributes=True)

    roles: list[GetRoleListDetails] | list[str] | None = None

    @model_validator(mode='after')
    def handel(self) -> Self:
        """Dealing with sectors and roles"""
        dept = self.dept
        if dept:
            self.dept = dept.name  # type: ignore
        roles = self.roles
        if roles:
            self.roles = [{"name":role.name} for role in roles]  # type: ignore
        return self


class CurrentUserIns(GetUserInfoListDetails):
    model_config = ConfigDict(from_attributes=True)


class UpdatePasswordParam(SchemaBase):
    old_password: str
    new_password: str
    confirm_password: str
