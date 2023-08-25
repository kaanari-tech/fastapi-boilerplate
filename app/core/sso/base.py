from typing import List

from httpx import AsyncClient

from schemas import OAuthCodeResponseSchema
from schemas import OAuthRedirectLink
from schemas import OAuthTokenResponseSchema
from schemas import OAuthUserDataResponseSchema


class OAuthBase:
    session: AsyncClient
    client_id: str
    secret_key: str
    webhook_redirect_uri: str

    scope: List[str]
    response_type: str = "code"

    def __init__(
        self,
        session: AsyncClient,
        client_id: str,
        secret_key: str,
        webhook_redirect_uri: str,
    ) -> None:
        self.session = session
        self.client_id = client_id
        self.secret_key = secret_key
        self.webhook_redirect_uri = webhook_redirect_uri

    def scope_to_str(self, delimiter: str = "%20") -> str:
        """
        Convert a scope list to string representation
        Replacing spaces with encoded spaces% 20 for pydantic model validation
        """

        return f"{delimiter}".join(self.scope)

    def prepare_user_data(
        self, external_id: str, user_data: dict
    ) -> OAuthUserDataResponseSchema:
        """Converting interface socials for the general data format of the system"""

        raise NotImplementedError

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.
        It is necessary for the user to further enter the service and receive a confirmation code from the service on Webhook.
        """

        raise NotImplementedError

    async def get_token(
        self, code: OAuthCodeResponseSchema
    ) -> OAuthTokenResponseSchema:
        """Exchange of a confirmation code for a user token."""

        raise NotImplementedError

    async def get_user_data(
        self, token: OAuthTokenResponseSchema
    ) -> OAuthUserDataResponseSchema:
        """ "Getting information about a user through an access token."""

        raise NotImplementedError
