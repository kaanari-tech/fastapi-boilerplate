from typing import Optional
from pydantic import AnyHttpUrl, BaseModel, EmailStr
from enum import Enum


class SocialTypes(Enum):
    facebook = "facebook"
    google = "google"
    msal = "msal"
    linkedin = "linkedin" 

class OAuthRedirectLink(BaseModel):
    url: AnyHttpUrl


class OAuthCodeResponseSchema(BaseModel):
    code: str


class OAuthTokenResponseSchema(BaseModel):
    token: str


class OAuthUserDataResponseSchema(BaseModel):
    external_id: str
    email: EmailStr
    social_type: SocialTypes
    img: Optional[AnyHttpUrl]
    firstname: Optional[str]
    lastname: Optional[str]
