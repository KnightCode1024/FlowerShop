# tests/integrations/conftest.py
import random
import asyncio
from typing import AsyncGenerator

import pytest
import httpx
from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.ext.asyncio import async_sessionmaker as AsyncSessionMaker

from decimal import Decimal

from entrypoint.config import config
from models import RoleEnum, Base
from repositories import UserRepository, ProductRepository, CategoryRepository
from schemas.category import CategoryCreate
from schemas.product import ProductCreate
from schemas.user import UserLogin, UserCreate, UserCreateConsole
from services import EmailService
from utils.strings import make_valid_password
from run import make_app

from dishka import Provider, provide, Scope

# Если хотите тестировать на той же БД, что в config — оставляем ниже DSN.
# Для изоляции тестов лучше указать тестовый DSN (sqlite in-memory или тестовый postgres).
TEST_DATABASE_DSN = config.database.DATABASE_URI  # или "sqlite+aiosqlite:///:memory:"

TABLES = ["categories", "users", "orders", "products", "promocodes", "product_images"]


@pytest.fixture(scope="session")
async def async_engine() -> AsyncEngine:
    """
    Создаём engine один раз на сессию тестов.
    """
    engine = create_async_engine(
        TEST_DATABASE_DSN,
        pool_pre_ping=True,
        echo=False,
        future=True,
    )
    # создаём схему (drop/create) — осторожно: это трогает БД из config
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def async_session_maker(async_engine: AsyncEngine) -> AsyncSessionMaker[AsyncSession]:
    """
    Передаём maker в тесты и в provider приложения.
    """
    return async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def database_provider(async_session_maker) -> Provider:
    """
    Test Database Provider для Dishka — выдаёт новую сессию на каждый REQUEST-скоуп.
    Это критично, чтобы тест и приложение не делили один AsyncSession.
    """

    class TestDatabaseProvider(Provider):
        @provide(scope=Scope.REQUEST)
        async def session(self) -> AsyncGenerator[AsyncSession, None]:
            async with async_session_maker() as s:
                yield s

    return TestDatabaseProvider()


@pytest.fixture
async def app(database_provider):
    """
    Создаём app, передаём тестовый database_provider в DI.
    make_app примет провайдер и создаст container с ним.
    """
    app = make_app(database_provider)
    return app


@pytest.fixture
async def client(app):
    """
    AsyncClient с ASGITransport — запускает lifespan(app) и Dishka контейнер.
    base_url может быть любым, т.к. ASGITransport рулит обработкой запросов локально.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def session(async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    """
    Удобная тестовая сессия: отдельная сессия на каждый тест.
    Используйте эту сессию для прямой записи в БД в тестах (commit и закрытие до HTTP-запроса).
    """
    async with async_session_maker() as s:
        yield s


# ---- репозитории и фабрики данных ----

@pytest.fixture
async def user_repository(session: AsyncSession):
    return UserRepository(session=session)


@pytest.fixture
async def category_repository(session: AsyncSession):
    return CategoryRepository(session=session)


@pytest.fixture
async def category_for_products(category_repository: CategoryRepository):
    category_data = CategoryCreate(name="Flowers")
    return await category_repository.create(category_data)


@pytest.fixture
def test_product1(category_for_products):
    return ProductCreate(
        name="Rose Bouquet",
        description="Beautiful red roses",
        price=Decimal("29.99"),
        in_stock=True,
        category_id=category_for_products.id,
    )


@pytest.fixture
async def product_repository(session: AsyncSession):
    return ProductRepository(session=session)


@pytest.fixture
async def created_product(product_repository, test_product1):
    return await product_repository.create(test_product1)


@pytest.fixture
async def email_service():
    # EmailService не использует сессию, можно вернуть реальную/заглушку
    return EmailService(config)


# ---- создание клиентов с пользователями (без резолва service из DI) ----
# Мы создаём пользователей через репозиторий и коммитим, затем используем client для HTTP-логина.
# Важно: commit/close сессии до POST, чтобы приложение видело изменения в БД.

@pytest.fixture
async def created_admin_client(client: AsyncClient, user_repository: UserRepository, session: AsyncSession):
    user_create_data = UserCreate(
        email=f"ADMIN_adminov{random.randint(1, 10000)}@test.com",
        username="admin",
        password=make_valid_password(12),
        role=RoleEnum.ADMIN,
        email_verified=True
    )
    user = await user_repository.create(user_create_data)
    await session.commit()  # важно — фиксация перед запросом к app

    assert user.email == user_create_data.email

    login_data = UserLogin(email=user_create_data.email, password=user_create_data.password)
    # Используем относительный путь — ASGITransport обрабатывает локально
    response = await client.post("/users/login", json=login_data.model_dump())
    assert response.status_code == 200, f"login failed: {response.text}"

    client.cookies.set("access_token", response.json()["access_token"])
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    client.cookies.set("refresh_token", response.json()["refresh_token"])

    return client


@pytest.fixture
async def created_user_client(client: AsyncClient, user_repository: UserRepository, session: AsyncSession):
    user_create_data = UserCreate(
        email=f"User{random.randint(1, 10000)}@test.com",
        username="user",
        password=make_valid_password(12),
        role=RoleEnum.USER,
        email_verified=True
    )
    user = await user_repository.create(user_create_data)
    await session.commit()

    assert user.email == user_create_data.email

    login_data = UserLogin(email=user_create_data.email, password=user_create_data.password)
    response = await client.post("/users/login", json=login_data.model_dump())
    assert response.status_code == 200

    client.cookies.set("access_token", response.json()["access_token"])
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    client.cookies.set("refresh_token", response.json()["refresh_token"])

    return client


@pytest.fixture
async def created_employee_client(client: AsyncClient, user_repository: UserRepository, session: AsyncSession):
    user_create_data = UserCreate(
        email=f"employee_{random.randint(1, 10000)}@test.com",
        username="employee",
        password=make_valid_password(12),
        role=RoleEnum.EMPLOYEE,
        email_verified=True
    )
    user = await user_repository.create(user_create_data)
    await session.commit()

    assert user.email == user_create_data.email

    login_data = UserLogin(email=user_create_data.email, password=user_create_data.password)
    response = await client.post("/users/login", json=login_data.model_dump())
    assert response.status_code == 200

    client.cookies.set("access_token", response.json()["access_token"])
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    client.cookies.set("refresh_token", response.json()["refresh_token"])

    return client
