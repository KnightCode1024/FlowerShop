import random
from typing import AsyncGenerator

import pytest
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
from schemas.user import UserLogin, UserCreate
from services import EmailService
from utils.strings import make_valid_password
from run import make_app

from dishka import Provider, provide, Scope

TEST_DATABASE_DSN = config.database.DATABASE_URI

TABLES = ["categories", "users", "orders", "products", "promocodes", "product_images"]


@pytest.fixture(scope="session")
async def async_engine() -> AsyncEngine:
    engine = create_async_engine(
        TEST_DATABASE_DSN,
        pool_pre_ping=True,
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def async_session_maker(async_engine: AsyncEngine) -> AsyncSessionMaker[AsyncSession]:
    return async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def database_provider(async_session_maker) -> Provider:
    class TestDatabaseProvider(Provider):
        @provide(scope=Scope.REQUEST)
        async def session(self) -> AsyncGenerator[AsyncSession, None]:
            async with async_session_maker() as s:
                yield s

    return TestDatabaseProvider()


@pytest.fixture
async def app(database_provider):
    app = make_app(database_provider)
    return app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def session(async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as s:
        yield s



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
    return EmailService(config)



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
    await session.commit()

    assert user.email == user_create_data.email

    login_data = UserLogin(email=user_create_data.email, password=user_create_data.password)
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
