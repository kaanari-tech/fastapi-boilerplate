import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    TITLE: str = "FASTAPI-BOILERPLATE"
    ENV: str = "dev"
    BASE_URL: str = "/api/v1"
    DEBUG: bool = False
    VERSION: str = "0.0.1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:3333",
    ]
    API_URL: str
    API_BASE_URL: str
    ROOT_DIR_PATH: str = str(Path(__file__).parent.parent.parent.absolute())

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    PUBLIC_KEY_PATH: str
    PRIVATE_KEY_PATH: str

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_TEMPLATES_DIR: str = os.getcwd() + "/app/templates"

    def load_key_file(self, key_file_path: str) -> str:
        try:
            with open(key_file_path, "r") as key_file:
                return key_file.read()
        except FileNotFoundError:
            raise ValueError(f"Key file not found at {key_file_path}")

    @property
    def PRIVATE_KEY_CONTENT(self) -> str:
        return self.load_key_file(self.PRIVATE_KEY_PATH)

    @property
    def PUBLIC_KEY_CONTENT(self) -> str:
        return self.load_key_file(self.PUBLIC_KEY_PATH)

    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER_NAME: str
    DB_PASSWORD: str

    RABBIT_MQ_HOST: str
    RABBIT_MQ_PORT: int
    RABBIT_MQ_PASSWORD: str
    RABBIT_MQ_USER: str

    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43800  # 1 month

    SECRET_KEY: str
    MIGRATIONS_DIR_PATH: str = os.path.join(ROOT_DIR_PATH, "alembic")

    def get_database_url(self, is_async: bool = False) -> str:
        if is_async:
            return (
                "postgresql+asyncpg://"
                f"{self.DB_USER_NAME}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        else:
            return (
                "postgresql://"
                f"{self.DB_USER_NAME}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

    APPLE_CLIENT_ID: str
    APPLE_SECRET_KEY: str
    APPLE_WEBHOOK_OAUTH_REDIRECT_URI: str

    FACEBOOK_CLIENT_ID: str
    FACEBOOK_SECRET_KEY: str
    FACEBOOK_WEBHOOK_OAUTH_REDIRECT_URI: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_SECRET_KEY: str
    GOOGLE_WEBHOOK_OAUTH_REDIRECT_URI: str

    LINKEDIN_CLIENT_ID: str
    LINKEDIN_SECRET_KEY: str
    LINKEDIN_WEBHOOK_OAUTH_REDIRECT_URI: str

    MSAL_CLIENT_ID: str
    MSAL_CLIENT_SECRET: str
    MSAL_WEBHOOK_OAUTH_REDIRECT_URI: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
