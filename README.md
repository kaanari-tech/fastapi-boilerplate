# FastAPI REST API boilerplate

## Description <!-- omit in toc -->

FastAPI REST boilerplate for typical project

## Table of Contents <!-- omit in toc -->

- [Features](#features)
- [Project structure](#project-structure)
- [Environmnent variables](#environmnent-variables)
- [Quick run](#quick-run)
- [Comfortable development](#comfortable-development)
- [Links](#links)
- [Database utils](#database-utils)
<!-- - [Tests](#tests)
- [Tests in Docker](#tests-in-docker)
- [Test benchmarking](#test-benchmarking) -->

## Features

- [x] Precommit ([Pre-commit](https://pre-commit.com/))
- [x] Config Service ([Pydantic](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)).
- [x] Database ([Sqlalchemy](https://www.sqlalchemy.org)).
- [x] Database migration ([Alembic](https://alembic.sqlalchemy.org))
- [x] Swagger.
- [x] Redoc.
- [x] Sign in and sign up via email.
- [x] Social sign in (apple, facebook, google, linkedin, microsoft)
- [x] Seeding ([sqlalchemyseed](https://sqlalchemyseed.readthedocs.io/en/stable/)).
- [x] Mailing
- [ ] Realtime notification using messaging queue and websockets
- [ ] File uploads
- [ ] Admin and User roles using RBAC ([Casbin](https://casbin.org/fr/docs/rbac)).
- [ ] I18N
- [ ] Elasticseach - logstash
- [ ] E2E and units tests.
- [ ] Monitoring using grafana and prometheus ([Grafana](https://grafana.com/))
- [ ] Docker.
- [ ] CI ([Gitlab](https://docs.gitlab.com/ee/ci/)).

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
│   │   └── v2
│   │   └── ...
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

befor starting you need to generate RSA key pairs, both public and private keys.
You can use [this website](https://travistidwell.com) or any other method you prefer to generate these keys.
Keep a note of the file paths where you save these keys on your project folder (like `private_key.pem` and `public_key.pem`) or local machine.


- `ENV` : Running Environment
- `API_BASE_URL`: The pathname of the api version url
- `DB_HOST`: Postgres database host
- `DB_PORT`: Postgres database port
- `DB_NAME`: Postgres database name
- `DB_USER_NAME`: Postgres user
- `DB_PASSWORD`: Postgres password
- `SECRET_KEY`: Postgres password
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token duration
- `PRIVATE_KEY_PATH`: Specify the absolute file paths to the RSA private key you generated earlier (`private_key.pem` if you saved it in your project root folder)
- `PUBLIC_KEY_PATH`: Specify the absolute file paths to the RSA public key you generated earlier (`public_key.pem` if you saved it in your project root folder)
- `SMTP_TLS`: Indicates whether to use TLS (true or false) for SMTP email communication.
- `SMTP_PORT`: The port number for SMTP email communication.
- `SMTP_HOST`: The hostname or IP address of the SMTP server for sending emails.
- `SMTP_USER`: The username for authenticating with the SMTP server.
- `SMTP_PASSWORD`: The password for authenticating with the SMTP server.

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
- Redoc: <http://localhost:8001/redoc>
- Openapi json: <http://localhost:8001/api/v1/openapi.json>
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
poe drop-tables
```
