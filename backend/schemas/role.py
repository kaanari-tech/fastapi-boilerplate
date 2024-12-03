from datetime import datetime

from pydantic import  ConfigDict, Field

from backend.common.enums import  StatusType
from backend.common.schema import SchemaBase


class RoleSchemaBase(SchemaBase):
    name: str
    # data_scope: RoleDataScopeType = Field(
    #     default=RoleDataScopeType.custom, description='Permission ranges (1: all data permissions 2: custom data permissions)'
    # )
    status: StatusType = Field(default=StatusType.enable)
    remark: str | None = None


class CreateRoleParam(RoleSchemaBase):
    pass


class UpdateRoleParam(RoleSchemaBase):
    pass

class RoleDetail(SchemaBase):
    model_config = ConfigDict(from_attributes=True)
    name: str 

class GetRoleListDetails(RoleSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    x_id: str
    created_time: datetime
    updated_time: datetime | None = None
