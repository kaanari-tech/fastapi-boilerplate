import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

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
    API_BASE_URL: str
    ROOT_DIR_PATH: str = str(Path(__file__).parent.parent.parent.absolute())

    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER_NAME: str
    DB_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
