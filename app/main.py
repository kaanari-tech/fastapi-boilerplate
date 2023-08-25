from fastapi import FastAPI
from fastapi_versionizer.versionizer import versionize, api_version

from app.core.config import settings

app = FastAPI(
    title=f"[{settings.ENV}]{settings.TITLE}",
    debug=settings.DEBUG or False,
    # responses={
        
    # }
)

versions = versionize(
    app=app,
    prefix_format='/api/v{major}.{minor}',
    version_format='{major}.{minor}',
    default_version=(0,1),
    docs_url='/docs',
    redoc_url='/redoc',
    enable_latest=True,
    latest_prefix='/latest',
    sorted_routes=False,
)
