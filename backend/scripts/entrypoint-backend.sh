#!/bin/bash
set -e

echo "Starting backend initialization..."

# Set PYTHONPATH for both migrations and application
export PYTHONPATH=src

# Выполняем миграции
echo "Running database migrations..."
uv run alembic upgrade head

# Запускаем приложение
echo "Starting FastAPI application..."
exec uv run uvicorn run:make_app --factory --host 0.0.0.0 --port 8000 --reload
