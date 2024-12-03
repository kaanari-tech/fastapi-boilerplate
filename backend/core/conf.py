from functools import lru_cache
import os
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.path_conf import ApiV2Path


class Settings(BaseSettings):
    """Global Settings"""
    model_config = SettingsConfigDict(env_file=f'{ApiV2Path}/.env', env_file_encoding='utf-8', extra='ignore')

    APP_NAME: str = "api_v2"

    OTLP_GRPC_ENDPOINT: str

    # Env Config
    ENVIRONMENT: Literal['dev', 'preprod', 'prod'] = 'dev'

    # Env POSTGRES
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_ECHO: bool = False
    POSTGRES_DATABASE: str = 'postgres'
    CLIENT_URL: str = 'http://localhost:3000'

    GENAI_API_KEY: str

    # Env Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str | None = None
    REDIS_DATABASE: int
    
    # Env MinIO
    MINIO_ENDPOINT: str
    MINIO_PORT: int
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_CLOUD_URL: str
    
    # Env SMTP
    SMTP_TLS: str
    SMTP_PORT: str
    SMTP_HOST: str
    SMTP_USER: str
    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str
    SMTP_PASSWORD: str
    EMAIL_TEMPLATES_DIR: str = os.getcwd() + "/templates/build"

    # Env Token
    TOKEN_SECRET_KEY: str  # key secrets.token_urlsafe(32)

    # Env Opera Log
    OPERA_LOG_ENCRYPT_SECRET_KEY: str  # key os.urandom(32), need to use bytes.hex() method to convert to str

    # FastAPI
    FASTAPI_API_V1_PATH: str = '/api/v1'
    FASTAPI_TITLE: str = 'Boilerplate'
    FASTAPI_VERSION: str = '0.0.1'
    FASTAPI_DESCRIPTION: str = 'Boilerplate api'
    FASTAPI_DOCS_URL: str | None = f'{FASTAPI_API_V1_PATH}/docs'
    FASTAPI_REDOCS_URL: str | None = f'{FASTAPI_API_V1_PATH}/redocs'
    FASTAPI_OPENAPI_URL: str | None = f'{FASTAPI_API_V1_PATH}/openapi'
    FASTAPI_STATIC_FILES: bool = False
    
    @model_validator(mode='before')
    @classmethod
    def validate_openapi_url(cls, values):
        if values['ENVIRONMENT'] == 'prod':
            values['OPENAPI_URL'] = None
        return values



    # Redis
    REDIS_TIMEOUT: int = 5

    # Token
    TOKEN_ALGORITHM: str = 'HS256'  
    TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1 # expiration time in seconds
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # refresh token expiration time in seconds
    TOKEN_REDIS_PREFIX: str = 'boilerplate:token'
    USER_SECURE_TOKEN_REDIS_PREFIX: str = 'user:token'
    ADMIN_SECURE_TOKEN_REDIS_PREFIX: str = 'admin:token'
    COMPANY_SECURE_TOKEN_REDIS_PREFIX: str = 'company:token'
    TOKEN_REFRESH_REDIS_PREFIX: str = 'boilerplate:refresh_token'
    TOKEN_REQUEST_PATH_EXCLUDE: list[str] = [ # JWT / RBAC whitelisting
        f'/admin{FASTAPI_API_V1_PATH}/auth/login',
        f'/client{FASTAPI_API_V1_PATH}/auth/login',
        f'/company{FASTAPI_API_V1_PATH}/auth/login',
        f'/mentor{FASTAPI_API_V1_PATH}/auth/login',
        f'/admin{FASTAPI_API_V1_PATH}/auth/token/new',
        f'/client{FASTAPI_API_V1_PATH}/auth/token/new',
        f'/company{FASTAPI_API_V1_PATH}/auth/token/new',
        f'/mentor{FASTAPI_API_V1_PATH}/auth/token/new',
    ]

    # JWT
    JWT_USER_REDIS_PREFIX: str = 'boilerplate:user'
    JWT_COMPANY_REDIS_PREFIX: str = 'boilerplate:company'
    JWT_ADMIN_REDIS_PREFIX: str = 'boilerplate:admin'
    JWT_USER_REDIS_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7

    # Permission (RBAC)
    PERMISSION_MODE: Literal['casbin', 'role-menu'] = 'casbin'
    PERMISSION_REDIS_PREFIX: str = 'boilerplate:permission'

    # RBAC
    # Casbin
    RBAC_CASBIN_EXCLUDE: set[tuple[str, str]] = {
        ('POST', f'/admin{FASTAPI_API_V1_PATH}/auth/logout'),
        ('POST', f'/client{FASTAPI_API_V1_PATH}/auth/logout'),
        ('POST', f'/mentor{FASTAPI_API_V1_PATH}/auth/logout'),
        ('POST', f'/company{FASTAPI_API_V1_PATH}/auth/logout'),
        ('POST', f'/admin{FASTAPI_API_V1_PATH}/auth/token/new'),
        ('POST', f'/client{FASTAPI_API_V1_PATH}/auth/token/new'),
        ('POST', f'/mentor{FASTAPI_API_V1_PATH}/auth/token/new'),
        ('POST', f'/company{FASTAPI_API_V1_PATH}/auth/token/new'),
    }

    # Role-Menu
    RBAC_ROLE_MENU_EXCLUDE: list[str] = [
        'sys:monitor:redis',
        'sys:monitor:server',
    ]

    # Cookies
    COOKIE_REFRESH_TOKEN_KEY: str = 'boilerplate_refresh_token'
    COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS: int = TOKEN_REFRESH_EXPIRE_SECONDS

    # Log
    LOG_ROOT_LEVEL: str = 'NOTSET'
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_LOGURU_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_CID_DEFAULT_VALUE: str = '-'
    LOG_CID_UUID_LENGTH: int = 32  # must <= 32
    LOG_STDOUT_LEVEL: str = 'INFO'
    LOG_STDERR_LEVEL: str = 'ERROR'
    LOG_STDOUT_FILENAME: str = 'boilerplate_access.log'
    LOG_STDERR_FILENAME: str = 'boilerplate_error.log'

    # Middleware
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_ACCESS: bool = True

    # Trace ID
    TRACE_ID_REQUEST_HEADER_KEY: str = 'X-Request-ID'

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        'http://localhost:3000',   # Front-end address without the '/' at the end
        'https://myboilerplate.com',
        'https://myboilerplate.com',
        'https://www.myboilerplate.com',
        'http://www.myboilerplate.com',
        'www.myboilerplate.com',
    ]
    CORS_EXPOSE_HEADERS: list[str] = [
        TRACE_ID_REQUEST_HEADER_KEY,
    ]

    # DateTime
    DATETIME_TIMEZONE: str = 'Africa/Abidjan'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Request limiter
    REQUEST_LIMITER_REDIS_PREFIX: str = 'boilerplate:limiter'

    # Demo mode (Only GET, OPTIONS requests are allowed)
    DEMO_MODE: bool = False
    DEMO_MODE_EXCLUDE: set[tuple[str, str]] = {
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/login'),
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/logout'),
        ('GET', f'{FASTAPI_API_V1_PATH}/auth/captcha'),
    }

    # Ip location
    IP_LOCATION_PARSE: Literal['online', 'offline', 'false'] = 'online'
    IP_LOCATION_REDIS_PREFIX: str = 'boilerplate:ip:location'
    IP_LOCATION_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1  # expiration time in seconds

    # Opera log
    OPERA_LOG_PATH_EXCLUDE: list[str] = [
        '/favicon.ico',
        FASTAPI_DOCS_URL,
        FASTAPI_REDOCS_URL,
        FASTAPI_OPENAPI_URL,
        f'{FASTAPI_API_V1_PATH}/auth/login/swagger',
        f'{FASTAPI_API_V1_PATH}/oauth2/github/callback',
        f'{FASTAPI_API_V1_PATH}/oauth2/linux-do/callback',
    ]
    OPERA_LOG_ENCRYPT_TYPE: int = 1  # 0: AES (performance loss); 1: md5; 2: ItsDangerous; 3: no encryption, others: replace with ******
    OPERA_LOG_ENCRYPT_KEY_INCLUDE: list[str] = [  # Will encrypt the value corresponding to the interface entry parameter
        'password',
        'old_password',
        'new_password',
        'confirm_password',
    ]

    GOOGLE_CLIENT_ID: str
    GOOGLE_SECRET_KEY: str
    GOOGLE_WEBHOOK_OAUTH_REDIRECT_URI: str

@lru_cache
def get_settings() -> Settings:
    """Getting Global Configuration"""
    return Settings()


# Create a configuration instance
settings = get_settings()
