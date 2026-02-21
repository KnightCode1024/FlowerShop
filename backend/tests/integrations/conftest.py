import asyncio
import os
import random
from decimal import Decimal

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import event, StaticPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from entrypoint.ioc.engine import engine
from models import Base, RoleEnum
from repositories import UserRepository, ProductRepository
from schemas.product import ProductCreate
from schemas.user import UserCreate, UserLogin, UserResponse, UserCreateConsole
from utils.strings import generate_random_token

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture(scope="session")
def event_loop():
    """pytest-asyncio: session-scoped event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine():
    """
    Session-scoped engine. Detects sqlite in-memory and uses StaticPool so
    the in-memory DB is shared between connections in the same process.
    """
    if TEST_DATABASE_URL.startswith("sqlite"):
        engine = create_async_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_async_engine(TEST_DATABASE_URL)

    # create once (optional, per-test fixture will recreate before each test)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # teardown engine and drop schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def async_session_maker(async_engine) -> async_sessionmaker[AsyncSession]:
    """sessionmaker bound to the async engine"""
    return async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False)


@pytest.fixture(autouse=True, scope="function")
async def recreate_db_per_test(async_engine):
    """
    AUTOUSE fixture: перед каждым тестом пересоздаём схему (drop_all -> create_all).
    После теста дополнительно дропаем (чтобы не оставлять состояние).
    Это простая, надёжная очистка — работает с любым движком (sqlite/postgres).
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        # дополнительная очистка после теста
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(async_session_maker) -> AsyncSession:
    """
    Простая сессия для теста. Используйте её в тестах:
        async def test_x(session):
            ...
    Если нужно транзакционное поведение (rollback) — можно заменить на
    pattern с outer transaction + nested savepoint (см. комментарий ниже).
    """
    async with async_session_maker() as s:
        yield s
        await s.close()


@pytest.fixture
async def client(base_url="http://backend:8000/api"):
    async with httpx.AsyncClient(base_url=base_url) as client:
        yield client


@pytest.fixture
def user_factory(client):
    async def _create():
        register_data = UserCreate(email=f"test{random.randint(10000, 99999999)}@test.com", password="12345678A@", username="Alex")

        created_user = await client.post("/users/register", json=register_data.model_dump())

        assert created_user.status_code == 200
        assert created_user.json()["email"] == register_data.email

        login_data = UserLogin(email=register_data.email, password=register_data.password)

        response2 = await client.post("/users/login", json=login_data.model_dump())

        assert response2.status_code == 200

        client.cookies.set("access_token", response2.json()["access_token"])
        client.headers["Authorization"] = f"Bearer {response2.json()["access_token"]}"
        client.cookies.set("refresh_token", response2.json()["access_token"])

        assert response2.json()["access_token"] is not None
        assert response2.json()["refresh_token"] is not None

        return UserResponse(**created_user.json())

    return _create


@pytest.fixture
def test_product1(test_category_for_products):
    return ProductCreate(
        name="Rose Bouquet",
        description="Beautiful red roses",
        price=Decimal("29.99"),
        in_stock=True,
        category_id=test_category_for_products.id,
    )


@pytest.fixture
async def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session=session)


@pytest.fixture
async def product_repository(session: AsyncSession):
    return ProductRepository(session=session)


@pytest.fixture
async def created_product(product_repository: ProductRepository, test_product1):
    return await product_repository.create(test_product1)


@pytest.fixture
async def created_admin_client(client, user_repository):
    user_create_data = UserCreateConsole(
        email=f"ADMIN_adminov{random.randint(1, 10000)}@test.com",
        username="admin",
        password=generate_random_token(10) + "@",
        role=RoleEnum.ADMIN,
    )
    user = await user_repository.create(user_create_data)

    assert user_create_data.email == user.email

    login_data = UserLogin(email=user_create_data.email, password=user_create_data.password)
    response = await client.post("/users/login", json=login_data.model_dump())

    assert response.status_code == 200

    client.cookies.set("access_token", response.json()["access_token"])
    client.headers["Authorization"] = f"Bearer {response.json()["access_token"]}"
    client.cookies.set("refresh_token", response.json()["refresh_token"])

    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None

    return client


@pytest.fixture
async def created_user_client(client, user_repository):
    user_create_data = UserCreateConsole(
        email=f"User{random.randint(1, 10000)}@test.com",
        username="user",
        password=generate_random_token(10) + "@",
        role=RoleEnum.USER
    )
    user = await user_repository.create(user_create_data)

    assert user_create_data.email == user.email

    login_data = UserLogin(email=user_create_data.email, password=user_create_data.password)
    response = await client.post("/users/login", json=login_data.model_dump())

    assert response.status_code == 200

    client.cookies.set("access_token", response.json()["access_token"])
    client.headers["Authorization"] = f"Bearer {response.json()["access_token"]}"
    client.cookies.set("refresh_token", response.json()["refresh_token"])

    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None

    return client
