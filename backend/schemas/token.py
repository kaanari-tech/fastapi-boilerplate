from datetime import datetime
from typing import Any


from backend.common.schema import SchemaBase
from backend.common.enums import Secure_token_type


class GetRoleDetails(SchemaBase):
    name: str
    class Config:
        from_attributes = True
    
class ConnectedUserInfo(SchemaBase):

    id: int
    x_id: str
    profile_image: dict | None = None
    firstname: str | None = None
    lastname: str | None = None
    phone: str | None = None
    email: str
    roles: list[GetRoleDetails] | None = None
    country_code: str | None = None

    class Config:
        from_attributes = True

class ConnectedCompanyInfo(SchemaBase):
    id: int
    x_id: str
    name: str | None = None
    email: str
    logo: Any | None = None
    min_members: int | None = None
    max_members: int | None = None
    email_verified: bool | None = None
    country_code: str | None = None
    role: GetRoleDetails | None = None

    class Config:
        from_attributes = True

class GetSwaggerToken(SchemaBase):
    access_token: str
    token_type: str = 'Bearer'
    user: Any


class AccessTokenBase(SchemaBase):
    access_token: str
    access_token_type: str = 'Bearer'
    access_token_expire_time: datetime


class GetNewToken(AccessTokenBase):
    pass


class GetLoginToken(AccessTokenBase):
    user: ConnectedUserInfo
    pass


class GetCompanyLoginToken(AccessTokenBase):
    company: ConnectedCompanyInfo
    pass

class Secure_token(SchemaBase):
    token_type: Secure_token_type
    token: str
    user_x_id: str
    used: bool = False
    expiration: datetime | None = None