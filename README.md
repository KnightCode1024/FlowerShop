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
- `Redis` (Кеш для ограничителя запроов, брокер для TaskIQ)
- `TaskIQ` (Асинхронные задачи)
- `Pytest` (Тестирование приложения)
- `UV` (Управление зависимостями)
- `Ruff` (Линтер и форматировщик кода)
### Фронтенд
Пока фронтенд ещё не реализован.
 - `React`

## Запуск
### Предварительные требования
- Git
- Docker и Docker Compose
- Python 3.14+ (для локальной разработки)
- UV - менеджер пакетов
- Ruff - линтер и форматировщик кода (автоматически устанавливается через UV)

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

# Установка всех зависимостей
uv sync

# Запуск приложения через UV (рекомендуемый способ)
uv run python src/run.py

# Или через прямой запуск (нужно активировать виртуальное окружение)
# Linux/Mac
source .venv/bin/activate
# Windows
.venv/Scripts/activate

# Запуск с hot-reload для разработки
uv run uvicorn run:make_app --factory --host 0.0.0.0 --port 8000 --reload

# Запуск миграций БД
uv run alembic upgrade head
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


### 7) Работа с зависимостями через UV
```bash
cd backend

# Установка всех зависимостей (runtime + dev)
uv sync

# Установка только runtime зависимостей (для production)
uv sync --no-dev

# Добавление новой зависимости
uv add package-name

# Добавление dev зависимости
uv add --dev package-name

# Обновление всех зависимостей
uv lock --upgrade

# Проверка на уязвимости в зависимостях
uv run pip-audit
```

### 8) Линтинг и форматирование кода с Ruff
```bash
cd backend

# Проверка кода на ошибки и стиль
uv run ruff check src/

# Автоматическое исправление проблем
uv run ruff check src/ --fix

# Форматирование кода (автоматическое)
uv run ruff format src/

# Проверка конкретного файла
uv run ruff check src/routers/user_router.py

# Показать только ошибки (без предупреждений)
uv run ruff check src/ --select=E,F

# Создание новой миграции (автоматически отформатируется)
uv run alembic revision --autogenerate -m "Add new feature"
```

### 9) Тестирование приложения
```bash
cd backend
# Запуск тестов через uv
uv run pytest
```

## Архитектура
...

## Ресурсы
- http://127.0.0.1:5173 - `фронтенд`
- http://127.0.0.1:8000/docs - `документация API`
- http://127.0.0.1:9001 - `Веб консоль S3 хранилища (MinIO)`
