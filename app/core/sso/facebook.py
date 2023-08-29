from typing import Any

from fastapi import HTTPException
from fastapi import status
from httpx import AsyncClient
from pydantic_core import Url

from .base import OAuthBase
from app.core.config import settings
from app.schemas import OAuthCodeResponseSchema
from app.schemas import OAuthRedirectLink
from app.schemas import OAuthTokenResponseSchema
from app.schemas import OAuthUserDataResponseSchema
from app.schemas import SocialTypes


class FacebookOAuth(OAuthBase):
    """
    Config Facebook
    https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow?locale=ru_RU#exchangecode
    """

    scope = ["email", "public_profile"]

    user_fields = ["id", "first_name", "last_name", "email", "picture"]

    def prepare_user_data(
        self, external_id: str, user_data: dict[Any, Any]
    ) -> OAuthUserDataResponseSchema:
        """Converting interface socials for the general data format of the system"""

        return OAuthUserDataResponseSchema(
            external_id=external_id,
            email=user_data["email"],
            social_type=SocialTypes.facebook,
            firstname=user_data["first_name"],
            lastname=user_data["last_name"],
            img=None,
        )

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.
        It is necessary for the user to further enter the service
        and receive a confirmation code from the service on Webhook.
        """

        url = (
            f"https://www.facebook.com/v12.0/dialog/oauth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.webhook_redirect_uri}&"
            f"scope={self.scope_to_str(',')}&"
            f"response_type={self.response_type}"
        )

        return OAuthRedirectLink(url=Url(url=url))

    async def get_token(
        self, code: OAuthCodeResponseSchema
    ) -> OAuthTokenResponseSchema:
        """Exchange of a confirmation code for a user token."""
        response = await self.session.get(
            "https://graph.facebook.com/v12.0/oauth/access_token",
            params=dict(
                code=code.code,
                client_id=self.client_id,
                client_secret=self.secret_key,
                redirect_uri=self.webhook_redirect_uri,
            ),
        )
        token_data = response.json()
        if "error" in token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=token_data["error"]["message"],
            )

        return OAuthTokenResponseSchema(token=token_data["access_token"])

    async def get_user_data(
        self, token: OAuthTokenResponseSchema
    ) -> OAuthUserDataResponseSchema:
        """ "Getting information about a user through an access token."""

        response = await self.session.get(
            url="https://graph.facebook.com/me",
            params=dict(fields=",".join(self.user_fields), access_token=token.token),
        )
        user_data = response.json()

        return self.prepare_user_data(user_data["id"], user_data)

    async def verify_and_process(
        self, code: OAuthCodeResponseSchema
    ) -> OAuthUserDataResponseSchema:
        token = await self.get_token(code=code)
        datas = await self.get_user_data(token=token)
        return datas


facebook_oauth = FacebookOAuth(
    session=AsyncClient(),
    client_id=settings.FACEBOOK_CLIENT_ID,
    secret_key=settings.FACEBOOK_SECRET_KEY,
    webhook_redirect_uri=f"{settings.API_URL}{settings.API_VERSION_PATH} \
    {settings.FACEBOOK_WEBHOOK_OAUTH_REDIRECT_URI}",
)
