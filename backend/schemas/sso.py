from enum import Enum
from typing import Optional

from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import EmailStr


class SocialTypes(Enum):
    facebook = "facebook"
    google = "google"
    msal = "msal"
    linkedin = "linkedin"
    github = "github"
    gitlab = "gitlab"


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
