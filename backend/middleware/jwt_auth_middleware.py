from typing import Any

from fastapi import Request, Response
from fastapi.security.utils import get_authorization_scheme_param
from pydantic_core import from_json
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError
from starlette.requests import HTTPConnection

from backend.schemas.user import CurrentUserIns
from backend.common.exception.errors import TokenError
from backend.common.log import log
from backend.common.security import jwt
from backend.core.conf import settings
from backend.database.db_postgres import async_db_session
from backend.database.db_redis import redis_client
from backend.utils.serializers import MsgSpecJSONResponse, select_as_dict


class _AuthenticationError(AuthenticationError):
    """Rewrite internal authentication error class"""

    def __init__(self, *, code: int = None, msg: str = None, headers: dict[str, Any] | None = None):
        self.code = code
        self.msg = msg
        self.headers = headers


class JwtAuthMiddleware(AuthenticationBackend):
    """JWT Authentication Middleware"""

    @staticmethod
    def auth_exception_handler(conn: HTTPConnection, exc: _AuthenticationError) -> Response:
        """Override internal authentication error handling"""
        return MsgSpecJSONResponse(content={'code': exc.code, 'msg': exc.msg, 'data': None}, status_code=exc.code)

    async def authenticate(self, request: Request) -> tuple[AuthCredentials, CurrentUserIns] | None:
        token = request.headers.get('Authorization')
        if not token:
            return

        if request.url.path in settings.TOKEN_REQUEST_PATH_EXCLUDE:
            return

        scheme, token = get_authorization_scheme_param(token)
        if scheme.lower() != 'bearer':
            return

        try:
            sub = await jwt.jwt_authentication(token)
            cache_user = await redis_client.get(f'{settings.JWT_USER_REDIS_PREFIX}:{sub}')
            if not cache_user:
                async with async_db_session() as db:
                    current_user = await jwt.get_current_user(db, sub)
                    user = CurrentUserIns(**select_as_dict(current_user))
                    await redis_client.setex(
                        f'{settings.JWT_USER_REDIS_PREFIX}:{sub}',
                        settings.JWT_USER_REDIS_EXPIRE_SECONDS,
                        user.model_dump_json(),
                    )
            else:
                # TODO: it should be replaced with the use of model_validate_json
                # https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing
                user = CurrentUserIns.model_validate(from_json(cache_user, allow_partial=True))
        except TokenError as exc:
            raise _AuthenticationError(code=exc.code, msg=exc.detail, headers=exc.headers)
        except Exception as e:
            log.error(f'JWT Authorization Exception:{e}')
            raise _AuthenticationError(code=getattr(e, 'code', 500), msg=getattr(e, 'msg', 'Internal Server Error'))

        # Note that this return uses a non-standard mode, so some of the standard features will be lost when authentication is passed.
        # For standard return modes see: https://www.starlette.io/authentication/
        return AuthCredentials(['authenticated']), user

