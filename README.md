# FastAPI REST API boilerplate

## Description <!-- omit in toc -->

FastAPI REST boilerplate for typical project

## Table of Contents <!-- omit in toc -->

- [Features](#features)
- [Project structure](#project-structure)
- [Environmnent variables](#nvironmnent-variables)
- [Quick run](#quick-run)
- [Comfortable development](#comfortable-development)
- [Links](#links)
- [Database utils](#database-utils)
- [Tests](#tests)
- [Tests in Docker](#tests-in-docker)
- [Test benchmarking](#test-benchmarking)

## Features

- [x] Database ([Sqlalchemy](https://www.sqlalchemy.org)).
- [x] Config Service ([Pydantic](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)).
- [x] Precommit ([Pre-commit](https://pre-commit.com/))
- [x] Database migration ([Alembic](https://alembic.sqlalchemy.org))
- [x] Swagger.
- [x] Social sign in (apple, facebook, google, linkdin, microsoft)
- [ ] Seeding.
- [ ] Sign in and sign up via email.
- [ ] Mailing
- [ ] Monitoring
- [ ] Admin and User roles using RBAC ([Casbin](https://casbin.org/fr/docs/rbac)).
- [ ] I18N
- [ ] File uploads
- [ ] E2E and units tests.
- [ ] Docker.
- [ ] CI (Github Actions).

## Project Structure

```
seeder           # Configurtion for database seeding
migrations       # Alembic migration files
app              # Rest api files
app.core         # General components like config, security, types, role, etc...
app.db           # Database connection specific
app.crud         # CRUD for types from models
app.models       # Sqlalchemy models
app.schemas      # Pydantic models that used in crud or handlers
app.templates    # Html files for mails
app.endpoints    # Restapi endpoints files
```

```
├── app
|   |
│   ├── core
│   ├── crud
│   ├── db
│   ├── endpoints
│   │   ├── api.py
│   │   └── v1
│   ├── main.py
│   ├── models
│   ├── schemas
|   |
│   └── templates
|
├── migrations
├── seeder
|── .vscode

```

## Environmnent variables
To correctly run the project, you will need some environment variables. Expose & import them in core/config.py

- `ENV` : Running Environment
- `API_BASE_URL`: The pathname of the api version url
- `DB_HOST`: Postgres database host
- `DB_PORT`: Postgres database port
- `DB_NAME`: Postgres database name
- `DB_USER_NAME`: Postgres user
- `DB_PASSWORD`: Postgres password
- `SECRET_KEY`: Postgres password


## Quick run

```bash
git clone --depth 1 https://github.com/kaanari-tech/fastapi-boilerplate.git my-app
cd my-app/
cp .env.example .env
docker-compose up -d --build
```

For check status run

```bash
docker-compose logs
```

## Comfortable development

```bash
git clone --depth 1 https://github.com/kaanari-tech/fastapi-boilerplate.git my-app
cd my-app/
cp .env.example .env
```

Change `DATABASE_HOST=postgres` to `DATABASE_HOST=localhost`
make sure you have [poetry](https://python-poetry.org) install
Run additional container:

```bash
docker-compose up -d postgres-db
poetry install
poe migrate
poetry run uvicorn app.main:app --port 8001 --host 0.0.0.0 --reload
```

## Links

- Swagger: <http://localhost:8001/docs>
- Adminer (client for DB): <http://localhost:8080>

## Database utils

Generate migration

```bash
poe makemigrations
```

Run migration

```bash
poe migrate
```

Revert migration

```bash
poe dwngrade
```

Drop all tables in database

```bash
poe drop-all-tables
```
