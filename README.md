# FlowerShop

Интернет магазин для продажи цветов

## Функционал
- REST API
    - CRUD операции на товаром
    - CRUD операции над категорией товара
    - JWT автоизация (регистрация, вход, обновление токена, профиль, все пользователи)
- Frontend
- ...

## Запуск

### Предварительные требования

- Python 3.14
- Docker и Docker Compose
- Git

### 1. Клонирование репозитория

```bash
git clone git@github.com:KnightCode1024/FlowerShop.git
cd FlowerShop
```

### 2. Настройка переменных окружения

Создайте файл `.env` в дириктории  `backend_flower_shop`:

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
```

### 3. Сборка и запуск через Docker

```bash
# Запуск и сборка
docker-compose up --build -d
# Повторный запуск
docker-compose up --build -d
```

### 4. Тестирование приложения
...

## Архитектура приложения

FlowerShop/
├── backend_flower_shop/          # REST API
│   ├── src/                      # Исходный код
│   │   ├── core/                 # Ядро приложения
│   │   ├── models/               # Модели базы данных
│   │   ├── schemas/              # Pydantic схемы
│   │   ├── services/             # Бизнес-логика
│   │   ├── repositories/         # Работа с данными
│   │   ├── routers/              # API маршруты
│   │   ├── utils/                # Вспомогательные функии
│   │   └── main.py               # Точка входа
│   ├── tests/                    # Тесты
│   └── alembic/                  # Миграции БД
├── frontend_flower_shop/         # Frontend React приложение
├── compose.yml                   # Docker Compose
└── README.md                     # README

## Ресурсы
## API Документация

После запуска сервера документация API доступна по адресу:
http://127.0.0.1:8000/docs

## Ресурсы проекта

- http://127.0.0.1:5173 - фронтенд
- http://127.0.0.1:8000/docs - документация API
- http://127.0.0.1:9001 - консоль S3 хранилища (MinIO)
