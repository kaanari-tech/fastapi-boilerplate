from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Depends, FastAPI, APIRouter
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from starlette.middleware.authentication import AuthenticationMiddleware

from backend.utils.prometheus import PrometheusMiddleware
from backend.common.exception.exception_handler import register_exception
from backend.common.log import set_customize_logfile, setup_logging
from backend.core.conf import settings
from backend.core.path_conf import STATIC_DIR
from backend.database.db_postgres import create_table
from backend.database.db_redis import redis_client
from backend.middleware.jwt_auth_middleware import JwtAuthMiddleware
from backend.middleware.opera_log_middleware import OperaLogMiddleware
from backend.middleware.state_middleware import StateMiddleware
from backend.middleware.i18n_middleware import I18nMiddleware
from backend.utils.demo_site import demo_site
from backend.utils.health_check import ensure_unique_route_names, http_limit_callback
from backend.utils.serializers import MsgSpecJSONResponse




@asynccontextmanager
async def register_init(app: FastAPI):
    """
    Start initialization

    :return:
    """
    # Creating Database Tables
    await create_table()
    # Connecting to redis
    await redis_client.open()
    # Initialize limiter
    await FastAPILimiter.init(
        redis=redis_client,
        prefix=settings.REQUEST_LIMITER_REDIS_PREFIX,
        http_callback=http_limit_callback,
    )

    yield

    # Closing a redis connection
    await redis_client.close()
    # Close limiter
    await FastAPILimiter.close()


def register_app(router: APIRouter, name: str = "Parse name" ) -> FastAPI:
    # FastAPI
    app = FastAPI(
        title=f"[{settings.ENVIRONMENT.upper()}] {settings.FASTAPI_TITLE} {name.upper()}",
        contact={
            "name": "Kaanari boilerplate",
            "email": "admin@kaanari.com",
        },
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        docs_url=f"{settings.FASTAPI_DOCS_URL}",
        redoc_url=f"{settings.FASTAPI_REDOCS_URL}",
        openapi_url=f"{settings.FASTAPI_OPENAPI_URL}",
        default_response_class=MsgSpecJSONResponse,
        lifespan=register_init,
    )

    # log (computing)
    register_logger()

    # Static files
    register_static_file(app)

    # middleware
    register_middleware(app, name)

    # routing (in computer networks)
    register_router(app, router)
    
    # tab window (in a web browser etc)
    register_page(app)

    # Global Exception Handling
    register_exception(app)
    return app


def register_logger() -> None:
    """
    System Log

    :return:
    """
    setup_logging()
    set_customize_logfile()


def register_static_file(app: FastAPI):
    """
    Static file interaction development model, production using nginx static resource service

    :param app:
    :return:
    """
    if settings.FASTAPI_STATIC_FILES:
        import os

        from fastapi.staticfiles import StaticFiles

        if not os.path.exists(STATIC_DIR):
            os.mkdir(STATIC_DIR)
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def register_middleware(app: FastAPI, name: str = "Parse name"):
    """
    Middleware, execution order from bottom to top

    :param app:
    :return:
    """
    # Setting metrics middleware
    app.add_middleware(PrometheusMiddleware, app_name=settings.APP_NAME)
    
    # Opera log (required)
    app.add_middleware(OperaLogMiddleware)

    # I18N translation middleware
    app.add_middleware(I18nMiddleware)
    

    app.add_middleware(
        AuthenticationMiddleware, backend=JwtAuthMiddleware(), on_error=JwtAuthMiddleware.auth_exception_handler
    )
        
    # Access log
    if settings.MIDDLEWARE_ACCESS:
        from backend.middleware.access_middleware import AccessMiddleware

        app.add_middleware(AccessMiddleware)

    # State
    app.add_middleware(StateMiddleware)

    # Trace ID (required)
    app.add_middleware(CorrelationIdMiddleware, validator=False)
    
    # CORS: Always at the end
    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )


def register_router(app: FastAPI, router: APIRouter):
    """
    routing

    :param app: FastAPI
    :return:
    """
    dependencies = [Depends(demo_site)] if settings.DEMO_MODE else None

    # API
    app.include_router(router, dependencies=dependencies)

    # Extra
    ensure_unique_route_names(app)
    # simplify_operation_ids(app)


def register_page(app: FastAPI):
    """
    paging search

    :param app:
    :return:
    """
    add_pagination(app)
