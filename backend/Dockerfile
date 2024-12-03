FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y \
    locales \
    gcc \
    libpq-dev && \
    sed -i 's/# \(fr_FR.UTF-8 UTF-8\)/\1/' /etc/locale.gen && \
    locale-gen && \
    apt-get clean

ENV LANG=fr_FR.UTF-8 \
    LANGUAGE=fr_FR.UTF-8 \
    LC_ALL=fr_FR.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN pip install --no-cache-dir poetry

COPY backend/pyproject.toml backend/poetry.lock* /app/

RUN poetry config virtualenvs.create false

RUN poetry install --no-root --no-dev

COPY . /app

# RUN [ -f .env.exemple ] && cp .env.exemple .env || touch .env

EXPOSE 8000


RUN chmod +x ./backend/entrypoint-api.sh

ENTRYPOINT ["bash","./backend/entrypoint-api.sh"]
