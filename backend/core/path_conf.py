import os

from pathlib import Path

# Get the project root directory
# Or use an absolute path to the backend directory, e.g. windows: BasePath = D:\git_project\fastapi_mysql\backend
BasePath = Path(__file__).resolve().parent.parent

ApiV2Path = Path(__file__).resolve().parent.parent.parent

# alembic migration file storage path
ALEMBIC_Versions_DIR = os.path.join(BasePath, 'alembic', 'versions')

# Log file path
LOG_DIR = os.path.join(BasePath, 'log')

# Offline IP Database Path
IP2REGION_XDB = os.path.join(BasePath, 'static', 'ip2region.xdb')

# Mount the static directory
STATIC_DIR = os.path.join(BasePath, 'static')

# jinja2 template file path
JINJA2_TEMPLATE_DIR = os.path.join(BasePath, 'templates')
