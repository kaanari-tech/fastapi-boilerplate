FROM python:3.11

WORKDIR /app/

# Install Poetry
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
#     cd /usr/local/bin && \
#     ln -s /opt/poetry/bin/poetry && \
#     poetry config virtualenvs.create false

# use built-in pip to access poetry
RUN pip install poetry

# start installing things with poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install

COPY ./pyproject.toml ./poetry.lock* /app/

RUN bash -c "poetry install --no-root --no-dev"

COPY . /app
ENV PYTHONPATH=/app

RUN cp .env.exemple .env

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get install libpq-dev -y \
    && apt-get clean

EXPOSE 81

CMD poetry run uvicorn main:app --host=0.0.0.0 --port=81
