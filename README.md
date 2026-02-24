# FlowerShop
Fullstack приложение интернет магазина цветов (FastAPI + React)

- [Функционал](#функционал)
- [Технологии](#технологии)
- [Запуск](#запуск)
- [Архитектура](#архитектура)
- [Ресурсы](#ресурсы)

## Функционал
- REST API
    - CRUD операции на товаром
    - CRUD операции над категорией товара
    - JWT автоизация (регистрация, вход, обновление токена, профиль, все пользователи)
    - Ограничитель запросов
- Frontend

## Технологии
### Бэкенд
- `FastAPI` (HTTP фреймворк, роутинг)
- `Pydantic` (схемы валидации)
- `Dishka` (Внедрение зависимостей)
- `PostgreSQL` (БД)
- `SQLalchemy` (ORM для работы с БД)
- `Alembic` (Миграции БД)
- `MinIO` (S3 хранилище для храния фото товаров)
- `Taskiq` (Асинхронное выполнение задач)
- `RabbitMQ` (Брокер задач для Taskiq)
- `Redis` (Кеш для ограничителя запроов)
- `Pytest` (Тестирование приложения)
- `Black` (Форматирование кода)
- `Flake8` (Линтер кода)
- `Isort` (Сортировка импортов)
### Фронтенд
Пока фронтенд ещё не реализован.
 - `React`

## Запуск
### Предварительные требования
- Git
- Docker и Docker Compose
- Python 3.14+ (для локальной разработки)
- pip - менеджер пакетов Python (предустановлен)

### 1) Клонирование репозитория
```bash
git clone git@github.com:KnightCode1024/FlowerShop.git
cd FlowerShop
```

### 2) Создание сертификатов для jwt

```bash
# Перейти в папку бекенда
cd backend

# Создание папки для ключей
mkdir certs

# Переходим в папку для ключей
cd certs

# Генерация RSA приватного ключа
openssl genrsa -out jwt-private.pem 2048

# Генерация публичного ключа
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```


### 3) Настройка переменных окружения
Создайте файл `.env` в дириктории  `backend`.

Вам может понадобится секретный ключ, для этого есть скрипт `secuirity.py` в папке `backend/srcripts/secuirity.py`. Запустите скрипт для генерации секретного ключа.

```env
# Настройки БД
POSTGRES_NAME=flower_shop_db
POSTGRES_USER=flower_shop_user
POSTGRES_PASSWORD=12345678
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Настройки приложения
APP_HOST=0.0.0.0
APP_PORT=8000
APP_SECRET_KEY=secret_key

# Настройки S3 хранилица
S3_ENDPOINT=http://minio:9000
S3_PUBLIC_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=admin
S3_SECRET_KEY=secret_key
S3_BUCKET_NAME=flower-shop
S3_REGION=us-east-1

REDIS_PORT=6379
REDIS_PORT=redis
```

### 4) Локальная разработка (альтернатива Docker)
```bash
# Переход в папку бекенда
cd backend

# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements/prod.txt
pip install -r requirements/dev.txt  # для инструментов разработки
pip install -r requirements/test.txt # для тестирования

# Запуск приложения
python src/run.py

# Запуск с hot-reload для разработки
uvicorn run:make_app --factory --host 0.0.0.0 --port 8000 --reload

# Запуск миграций БД
alembic upgrade head
```

### 5) Сборка и запуск через Docker
```bash
# Запуск и сборка
docker-compose up --build -d
```

### 6) Создание пользователей
Для создания пользователей через консоль используйте скрипт (доступны все роли):

```bash
# Переход в docker контейнер бекенда
docker-compose exec backend sh
# Интерактивный режим
python src/create_user.pysrc
# Режим с аргументами
python src/create_user.py --email admin@example.com --username admin --role admin --password MySecurePass123!
# Показать справку
python src/create_user.py --help
```

### 7) Линтинг и форматирование кода
```bash
cd backend
# Убедитесь, что установлены dev зависимости
pip install -r requirements/dev.txt
# Форматирование кода (black)
black src/
# Проверка стиля кода (flake8)
flake8 src/
# Сортировка импортов (isort)
isort src/
# Создание новой миграции (автоматически отформатируется)
alembic revision --autogenerate -m "Add feature"
```

### 8) Тестирование приложения
```bash
cd backend

# Убедитесь, что установлены test зависимости
pip install -r requirements/test.txt

# Запуск тестов
pytest
```

## Архитектура
...

## Ресурсы
- http://127.0.0.1:5173 - `фронтенд`
- http://127.0.0.1:8000/docs - `документация API`
- http://127.0.0.1:9001 - `Веб консоль S3 хранилища (MinIO)`
