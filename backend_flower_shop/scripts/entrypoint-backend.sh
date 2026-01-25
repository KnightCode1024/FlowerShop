#!/bin/bash
set -e

echo "Starting backend initialization..."

# Выполняем миграции
echo "Running database migrations..."
alembic -c /backend_flower_shop/alembic.ini upgrade head

#  && uvicorn src.main:app --host 0.0.0.0 --port 8000

# Запускаем приложение
echo "Starting FastAPI application..."
exec python main.py
