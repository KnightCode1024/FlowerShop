# FlowerShop

Интернет магазин для продажи цветов

## Функционал

- Управление категориями товаров
- Управление товарами с изображениями
- REST API для взаимодействия с фронтендом
- Хранение изображений в S3-совместимом хранилище

## Быстрый запуск

### Предварительные требования

- Python 3.8+
- Docker и Docker Compose
- Git

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd FlowerShop
```

### 2. Установка зависимостей бэкенда

```bash
cd backend_flower_shop
pip install -e .
pip install -r requirements-dev.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` в директории `backend_flower_shop`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/flowershop
SECRET_KEY=your-secret-key-here
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=flowershop
```

### 4. Запуск инфраструктуры

```bash
# Из корневой директории проекта
docker-compose up -d
```

### 5. Запуск миграций базы данных

```bash
cd backend_flower_shop
alembic upgrade head
```

### 6. Запуск сервера

```bash
# Из директории backend_flower_shop
python run.py
# Или напрямую через uvicorn
uvicorn src.main:app --reload
```

### 7. Запуск тестов

```bash
# Из директории backend_flower_shop
pytest
```

## Структура проекта

```
FlowerShop/
├── backend_flower_shop/          # Backend API
│   ├── src/                      # Исходный код
│   │   ├── core/                 # Ядро приложения
│   │   ├── models/               # Модели базы данных
│   │   ├── schemas/              # Pydantic схемы
│   │   ├── services/             # Бизнес-логика
│   │   ├── repositories/         # Репозитории данных
│   │   ├── routers/              # API маршруты
│   │   └── main.py               # Точка входа
│   ├── tests/                    # Тесты
│   ├── alembic/                  # Миграции БД
│   └── setup.py                  # Конфигурация пакета
├── frontend_flower_shop/         # Frontend React приложение
├── compose.yml                   # Docker Compose
└── README.md                     # Эта документация
```

## API Документация

После запуска сервера документация API доступна по адресу:
http://127.0.0.1:8000/docs

## Ресурсы проекта

- http://127.0.0.1:5173 - фронтенд
- http://127.0.0.1:8000/docs - документация API
- http://127.0.0.1:9001 - консоль S3 хранилища (MinIO)

## Разработка

### Запуск тестов

```bash
cd backend_flower_shop
pytest
```

### Покрытие кода тестами

```bash
pytest --cov=services --cov-report=html
```

### Форматирование кода

```bash
black src/
isort src/
```

### Линтинг

```bash
flake8 src/
mypy src/
```