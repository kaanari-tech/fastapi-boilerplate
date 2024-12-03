from typing import Any

from fastapi import HTTPException
from fastapi import status
from httpx import AsyncClient
from pydantic_core import Url

from .base import OAuthBase
from backend.core.conf import settings
from backend.schemas.sso import OAuthCodeResponseSchema
from backend.schemas.sso import OAuthRedirectLink
from backend.schemas.sso import OAuthTokenResponseSchema
from backend.schemas.sso import OAuthUserDataResponseSchema
from backend.schemas.sso import SocialTypes


class GoogleOAuth(OAuthBase):
    """
    Config Google
    https://developers.google.com/identity/protocols/oauth2/web-server#httprest_3
    """

    scope = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    access_type = "offline"
    grand_type = "authorization_code"

    def generate_body_for_access_token(self, code: OAuthCodeResponseSchema) -> str:
        """
        Generating the request body to send to the service to receive the user's token.
        """

        return (
            f"code={code.code}&"
            f"client_id={self.client_id}&"
            f"client_secret={self.secret_key}&"
            f"grant_type={self.grand_type}&"
            f"redirect_uri={self.webhook_redirect_uri}"
        )

    def prepare_user_data(
        self, external_id: str, user_data: dict[Any, Any]
    ) -> OAuthUserDataResponseSchema:
        """Converting interface socials for the general data format of the system"""
        return OAuthUserDataResponseSchema(
            external_id=external_id,
            email=user_data["email"],
            social_type=SocialTypes.google,
            img=user_data["picture"],
            firstname=user_data["family_name"] if "family_name" in user_data else "",
            lastname=user_data["given_name"] if "given_name" in user_data else "",
        )

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.
        It is necessary for the user to further enter the service
        and receive a confirmation code from the service on Webhook.
        """

        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"scope={self.scope_to_str()}&"
            f"access_type={self.access_type}&"
            f"response_type={self.response_type}&"
            f"redirect_uri={self.webhook_redirect_uri}&"
            f"client_id={self.client_id}"
        )

        return OAuthRedirectLink(url=Url(url=url))

    async def get_token(
        self, code: OAuthCodeResponseSchema
    ) -> OAuthTokenResponseSchema:
        """Exchange of a confirmation code for a user token."""

        response = await self.session.post(
            url="https://oauth2.googleapis.com/token",
            content=self.generate_body_for_access_token(code),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_data = response.json()
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=token_data["error_description"],
            )
        token_data = response.json()

        return OAuthTokenResponseSchema(token=token_data["id_token"])

    async def get_user_data(
        self, token: OAuthTokenResponseSchema
    ) -> OAuthUserDataResponseSchema:
        """ "Getting information about a user through an access token."""

        response = await self.session.get(
            url="https://oauth2.googleapis.com/tokeninfo",
            params=dict(id_token=token.token),
        )
        user_data = response.json()
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=user_data["error_description"],
            )

        return self.prepare_user_data(user_data["sub"], user_data)

    async def verify_and_process(
        self, code: OAuthCodeResponseSchema
    ) -> OAuthUserDataResponseSchema:
        token = await self.get_token(code=code)
        datas = await self.get_user_data(token=token)
        return datas


google_oauth = GoogleOAuth(
    session=AsyncClient(),
    client_id=settings.GOOGLE_CLIENT_ID,
    secret_key=settings.GOOGLE_SECRET_KEY,
    webhook_redirect_uri=settings.GOOGLE_WEBHOOK_OAUTH_REDIRECT_URI,
)
