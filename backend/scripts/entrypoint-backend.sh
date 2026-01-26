#!/bin/bash
set -e

echo "Starting backend initialization..."

# Set PYTHONPATH for both migrations and application
export PYTHONPATH=src

# Выполняем миграции
echo "Running database migrations..."
alembic upgrade head

# Запускаем приложение
echo "Starting FastAPI application..."
exec uvicorn src.app.run:make_app --factory  --host 0.0.0.0 --port 8000 --reload
