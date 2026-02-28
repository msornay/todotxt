FROM python:3.11-slim

RUN pip install --no-cache-dir ruff pytest

WORKDIR /app
