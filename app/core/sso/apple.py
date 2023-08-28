from fastapi import HTTPException
from fastapi import status
from httpx import AsyncClient

from .base import OAuthBase
from app.core.config import settings
from app.models import OAuthCodeResponseSchema
from app.models import OAuthRedirectLink
from app.models import OAuthTokenResponseSchema
from app.models import OAuthUserDataResponseSchema


class AppleOAuth(OAuthBase):
    """
    Config apple
    https://developer.apple.com/documentation/sign_in_with_apple
    """

    scope = ["name", "email"]

    user_fields = ["id", "first_name", "last_name", "email"]

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.
        It is necessary for the user to further enter the service
        and receive a confirmation code from the service on Webhook.
        """

        url = (
            "https://appleid.apple.com/auth/authorize?"
            f"client_id={self.client_id}"
            f"redirect_uri={self.webhook_redirect_uri}&"
            f"response_type={self.response_type}&"
            f"scope={self.scope_to_str()}&"
        )
        return OAuthRedirectLink(url=url)

    async def get_token(
        self, code: OAuthCodeResponseSchema
    ) -> OAuthTokenResponseSchema:
        """Exchange of a confirmation code for a user token."""

        response = await self.session.get(
            "https://appleid.apple.com/auth/token",
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
            url="https://appleid.apple.com/auth/authorize?client_id=[CLIENT_ID]&redirect_uri=[REDIRECT_URL]& \
            response_type=codeid_token&state=[STATE]&scope=[SCOPES]&response_mode=form_post",
            params=dict(
                fields=",".join(self.user_fields),
                access_token=token.token,
            ),
        )
        user_data = response.json()

        return self.prepare_user_data(user_data["id"], user_data)


apple_oauth = AppleOAuth(
    session=AsyncClient(),
    client_id=settings.APPLE_CLIENT_ID,
    secret_key=settings.APPLE_SECRET_KEY,
    webhook_redirect_uri=settings.APPLE_WEBHOOK_OAUTH_REDIRECT_URI,
)
