#!/bin/bash
set -e

echo "Starting backend initialization..."

# Выполняем миграции
echo "Running database migrations..."
alembic upgrade head

# Запускаем приложение
echo "Starting FastAPI application..."
exec python main.py
