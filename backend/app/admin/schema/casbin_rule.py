from pydantic import ConfigDict, Field

from backend.common.enums import MethodType
from backend.common.schema import SchemaBase


class CreatePolicyParam(SchemaBase):
    sub: str = Field(..., description='User x_id / Role x_id')
    path: str = Field(..., description='api path')
    method: MethodType = Field(default=MethodType.GET, description='Request method')


class UpdatePolicyParam(CreatePolicyParam):
    pass


class DeletePolicyParam(CreatePolicyParam):
    pass


class DeleteAllPoliciesParam(SchemaBase):
    uuid: str | None = None
    role: str


class CreateUserRoleParam(SchemaBase):
    uuid: str = Field(..., description='User x_id')
    role: str = Field(..., description='role')


class DeleteUserRoleParam(CreateUserRoleParam):
    pass


class GetPolicyListDetails(SchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ptype: str = Field(..., description='Rule type, p / g')
    v0: str = Field(..., description='User uuid / Role')
    v1: str = Field(..., description='api path / roles')
    v2: str | None = None
    v3: str | None = None
    v4: str | None = None
    v5: str | None = None
