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


class LinkedinOAuth(OAuthBase):
    """
    Config linkedin
    https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2?context=linkedin%2Fconsumer%2Fcontext
    """

    scope = ["openid", "email", "profile"]

    def prepare_user_data(
        self, external_id: str, user_data: dict
    ) -> OAuthUserDataResponseSchema:
        """Converting interface socials for the general data format of the system"""

        return OAuthUserDataResponseSchema(
            external_id=external_id,
            email=user_data["email"],
            img=user_data["picture"],
            social_type=SocialTypes.linkedin,
            firstname=user_data["given_name"],
            lastname=user_data["family_name"],
        )

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.
        It is necessary for the user to further enter the service
        and receive a confirmation code from the service on Webhook.
        """

        url = (
            f"https://www.linkedin.com/oauth/v2/authorization?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.webhook_redirect_uri}&"
            f"scope={self.scope_to_str(',')}&"
            f"state=auth&"
            f"response_type={self.response_type}"
        )

        return OAuthRedirectLink(url=url)

    async def get_token(
        self, code: OAuthCodeResponseSchema
    ) -> OAuthTokenResponseSchema:
        """Exchange of a confirmation code for a user token."""
        response = await self.session.get(
            "https://www.linkedin.com/oauth/v2/accessToken",
            params=dict(
                grant_type="authorization_code",
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
                detail=token_data["error_description"],
            )

        return OAuthTokenResponseSchema(token=token_data["access_token"])

    async def get_user_data(
        self, token: OAuthTokenResponseSchema
    ) -> OAuthUserDataResponseSchema:
        """ "Getting information about a user through an access token."""

        response = await self.session.get(
            url="https://api.linkedin.com/v2/userinfo",
            headers=dict(Authorization=f"Bearer {token.token}"),
        )
        user_data = response.json()

        if "serviceErrorCode" in user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=user_data["message"]
            )

        return self.prepare_user_data(user_data["sub"], user_data)

    async def verify_and_process(self, code: str):
        token = await self.get_token(code=code)

        datas = await self.get_user_data(token=token)
        return datas


linkedin_oauth = LinkedinOAuth(
    session=AsyncClient(),
    client_id=settings.LINKEDIN_CLIENT_ID,
    secret_key=settings.LINKEDIN_SECRET_KEY,
    webhook_redirect_uri=f"{settings.API_URL}{settings.API_VERSION_PATH} \
        {settings.LINKEDIN_WEBHOOK_OAUTH_REDIRECT_URI}",
)
