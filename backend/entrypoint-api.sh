#!/bin/bash

# Set the locale environment variables
export LANG=fr_FR.UTF-8
export LANGUAGE=fr_FR.UTF-8
export LC_ALL=fr_FR.UTF-8

cd backend

# Appliquer les migrations de la base de données
poetry run alembic revision --autogenerate
poetry run alembic upgrade heads
# cd ..

# Démarrer l'application FastAPI avec Uvicorn sans le reloader
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000
# poetry run fastapi run
