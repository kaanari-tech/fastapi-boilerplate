from fastapi import HTTPException
from fastapi import status
from httpx import AsyncClient

from .base import OAuthBase
from app.core.config import settings
from app.schemas import OAuthCodeResponseSchema
from app.schemas import OAuthRedirectLink
from app.schemas import OAuthTokenResponseSchema
from app.schemas import OAuthUserDataResponseSchema
from app.schemas import SocialTypes


class MicrosoftOAuth(OAuthBase):
    """
    Config Microsoft
    https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow
    """

    scope = ["User.Read"]

    access_type = "offline"
    grand_type = "authorization_code"

    def generate_body_for_access_token(self, code: OAuthCodeResponseSchema) -> str:
        """
        Generating the request body to send to the service to receive the user's token.
        """

        return (
            f"code={code.code}&"
            f"client_id={self.client_id}&"
            f"scope={self.scope_to_str()}&"
            f"redirect_uri={self.webhook_redirect_uri}&"
            f"grant_type={self.grand_type}&"
            f"client_secret={self.secret_key}&"
        )

    def prepare_user_data(
        self, external_id: str, user_data: dict
    ) -> OAuthUserDataResponseSchema:
        """Converting interface socials for the general data format of the system"""

        return OAuthUserDataResponseSchema(
            external_id=external_id,
            email=user_data["userPrincipalName"],
            social_type=SocialTypes.msal,
            img=None,
            firstname=user_data["givenName"],
            lastname=user_data["surname"],
        )

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.
        It is necessary for the user to further enter the service
        and receive a confirmation code from the service on Webhook.
        """

        url = (
            "https://login.microsoftonline.com/"
            f"{settings.MSAL_TENANT_ID}/oauth2/v2.0/authorize?&"
            f"client_id={self.client_id}&"
            f"response_type={self.response_type}&"
            f"redirect_uri={self.webhook_redirect_uri}&"
            f"scope={self.scope_to_str()}"
        )

        return OAuthRedirectLink(url=url)

    async def get_token(
        self, code: OAuthCodeResponseSchema
    ) -> OAuthTokenResponseSchema:
        """Exchange of a confirmation code for a user token."""
        response = await self.session.post(
            url=f"https://login.microsoftonline.com/{settings.MSAL_TENANT_ID}/oauth2/v2.0/token",
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

        return OAuthTokenResponseSchema(token=token_data["access_token"])

    async def get_user_data(
        self, token: OAuthTokenResponseSchema
    ) -> OAuthUserDataResponseSchema:
        """ "Getting information about a user through an access token."""
        headers = {
            "Authorization": "Bearer {0}".format(token.token),
            "Content-Type": "application/json",
        }

        response = await self.session.get(
            url="https://graph.microsoft.com/v1.0/me", headers=headers
        )

        user_data = response.json()
        print(user_data)
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=user_data["error_description"],
            )

        return self.prepare_user_data(token.token, user_data)


microsoft_oauth = MicrosoftOAuth(
    session=AsyncClient(),
    client_id=settings.MSAL_CLIENT_ID,
    secret_key=settings.MSAL_CLIENT_SECRET,
    webhook_redirect_uri=settings.MSAL_WEBHOOK_OAUTH_REDIRECT_URI,
)
