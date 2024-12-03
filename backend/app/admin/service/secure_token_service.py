from datetime import datetime, timedelta
from backend.common.enums import Secure_token_type
from backend.common.exception import errors
from backend.common.security.sec_token import generate_secret_token
from backend.schemas.token import Secure_token
from backend.database.db_redis import redis_client
from backend.core.conf import settings




class Secure_tokenService:
    @staticmethod
    async def gen_token(user_x_id: str, type: Secure_token_type, expire: int | None = None) -> str:
        token = generate_secret_token()
        expiration=(datetime.now() + timedelta(minutes=expire)) if expire is not None else (datetime.now() + timedelta(minutes=5))
        password_reset_token = Secure_token(
            token=token,
            token_type=type,
            user_x_id=user_x_id,
            expiration=expiration,
        )
        
        add = await redis_client.set(
            f"{settings.USER_SECURE_TOKEN_REDIS_PREFIX}:{user_x_id}:{type.value}",
            password_reset_token.model_dump_json(),
            timedelta(minutes=expire) if expire is not None else None,
        )
        
        if not add:
            raise errors.ServerError(msg='Token generation failed')
        return token
    
    @staticmethod
    async def check_token(token: str, user_x_id: str, type: Secure_token_type) -> bool:
        rst_token = await redis_client.get(f"{settings.USER_SECURE_TOKEN_REDIS_PREFIX}:{user_x_id}:{type.value}")
        if not rst_token:
            raise errors.TokenError(msg='Token has expired')
        
        validate_token = Secure_token.model_validate_json(rst_token)

        if validate_token.used:
            raise errors.TokenError(msg='Token has been used')
        
        if validate_token.expiration < datetime.now():
            raise errors.TokenError(msg='Token has expired')
        if validate_token.token_type != type.value:
            raise errors.TokenError(msg='Token type is invalid')
        if validate_token.token != token:
            raise errors.TokenError(msg='Token user is invalid')
        
        validate_token.used = True
        await redis_client.set(
            f"{settings.USER_SECURE_TOKEN_REDIS_PREFIX}:{user_x_id}:{type.value}",
            validate_token.model_dump_json(),
        )
        print("validate_token =====>", validate_token.used)
        return True
    
secure_token_service = Secure_tokenService()