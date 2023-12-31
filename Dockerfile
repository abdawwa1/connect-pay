FROM python:3.9

RUN pip install --upgrade pip poetry

WORKDIR /app

COPY pyproject.toml pyproject.toml

RUN poetry config virtualenvs.create false && poetry install

COPY . /app
