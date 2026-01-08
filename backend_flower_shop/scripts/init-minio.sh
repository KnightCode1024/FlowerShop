#!/bin/bash

echo "Starting MinIO initialization..."

# Ждем полного запуска MinIO
sleep 5

# Настраиваем alias
mc alias set local http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" --api s3v4

# Проверяем подключение
echo "Testing MinIO connection..."
mc admin info local

# Создаем бакеты если их нет
echo "Creating buckets..."
mc mb local/"$S3_BUCKET_NAME" --ignore-existing
mc mb local/"$S3_BUCKET_NAME"-temp --ignore-existing

# Устанавливаем публичный доступ на чтение для основного бакета
echo "Setting public read access for bucket: $S3_BUCKET_NAME"
mc anonymous set download local/"$S3_BUCKET_NAME"

# Для временного бакета оставляем приватный доступ
mc anonymous set private local/"$S3_BUCKET_NAME"-temp

# Проверяем установленную политику
echo "Current bucket policy for $S3_BUCKET_NAME:"
mc anonymous get local/"$S3_BUCKET_NAME"

# Настраиваем CORS правильным способом
echo "Configuring CORS..."
cat > /tmp/cors-config.json << 'EOF'
{
  "cors": [
    {
      "allowed_origins": ["*"],
      "allowed_methods": ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
      "allowed_headers": ["Authorization", "Content-Type", "Accept", "Content-Disposition", "x-amz-date"],
      "expose_headers": ["ETag", "Content-Length", "Content-Disposition"],
      "max_age_seconds": 3600
    }
  ]
}
EOF

# Импортируем конфигурацию CORS
mc admin config import local < /tmp/cors-config.json

# Применяем конфигурацию без интерактивного TTY
mc admin service restart local --no-color

# Даем время на применение изменений
sleep 3

# Проверяем настройки CORS
echo "CORS configuration:"
mc admin config get local cors

# Создаем тестовый файл для проверки доступа
echo "Creating test file..."
echo "test content" > /tmp/test.txt
mc cp /tmp/test.txt local/"$S3_BUCKET_NAME"/test.txt

echo "=========================================="
echo "✅ MinIO initialization completed"
echo "📦 Bucket: $S3_BUCKET_NAME"
echo "🔗 Public URL example: http://localhost:9000/$S3_BUCKET_NAME/test.txt"
echo "🔧 Console: http://localhost:9001"
echo "👤 User: $MINIO_ROOT_USER"
echo "=========================================="

# Проверяем доступ к тестовому файлу
echo "Testing public access..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:9000/"$S3_BUCKET_NAME"/test.txt