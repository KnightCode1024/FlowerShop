#!/bin/bash
set -e

# Создаем необходимые директории
mkdir -p /data

# Запускаем MinIO в фоне
/usr/bin/minio server /data --console-address ":9001" &

# Ждем запуска MinIO
echo "Waiting for MinIO to start..."
until curl -s http://localhost:9000/minio/health/live > /dev/null; do
    sleep 2
done

echo "MinIO started, running initialization..."

# Ждем еще немного для стабильности
sleep 3

# Выполняем инициализацию
/init-minio.sh

# Ждем завершения MinIO
wait