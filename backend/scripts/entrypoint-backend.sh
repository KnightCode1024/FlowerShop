#!/bin/bash
set -e

echo "Starting backend initialization..."

# Выполняем миграции
# echo "Running database migrations..."
# alembic -c /backend/alembic.ini upgrade head

#  && uvicorn src.main:app --host 0.0.0.0 --port 8000

# Запускаем приложение
echo "Starting FastAPI application..."
export PYTHONPATH=src
exec uvicorn app.run:make_app --factory  --host 0.0.0.0 --port 8000 --reload
