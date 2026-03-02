import asyncio
import random
import httpx
import pytest
from httpx import ASGITransport

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from decimal import Decimal

from core.uow import UnitOfWork
from entrypoint.config import config
from entrypoint.ioc.engine import session_factory, engine
from models import RoleEnum
from repositories import UserRepository, ProductRepository, CategoryRepository
from run import make_app
from schemas.category import CategoryCreate
from schemas.product import ProductCreate
from schemas.user import UserLogin, UserCreateConsole, UserCreate
from services import UserService, EmailService
from utils.strings import make_valid_password
from run import make_app

TABLES = ["categories",
          "users",
          "orders",
          "products",
          "promocodes",
          "product_images"]


@pytest.fixture()
async def clear_db():
    async with engine.begin() as conn:
        for t in TABLES:
            await conn.exec_driver_sql(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE")
    yield


@pytest.fixture
async def app():
    return make_app()


@pytest.fixture
async def client(app):
    async with httpx.AsyncClient(base_url="http://backend:8000/api") as client:
        yield client


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
async def product_repository(session: AsyncSession):
    return ProductRepository(session=session)


@pytest.fixture
async def created_product(product_repository, test_product1):
    return await product_repository.create(test_product1)


@pytest.fixture
async def session() -> AsyncSession:
    async with session_factory() as s:
        yield s


@pytest.fixture
async def email_service(session: AsyncSession):
    return EmailService(config)


@pytest.fixture
async def created_admin_client(client, user_repository: UserRepository):
    user_create_data = UserCreate(
        email=f"ADMIN_adminov{random.randint(1, 10000)}@test.com",
        username="admin",
        password=make_valid_password(12),
        role=RoleEnum.ADMIN,
        email_verified=True
    )
    user = await user_repository.create(user_create_data)

    assert user_create_data.email == user.email

    login_data = UserLogin(email=user_create_data.email, password=user_create_data.password)
    response = await client.post("http://backend:8000/api/users/login", json=login_data.model_dump())

    print(response.text, response.headers, login_data)

    assert response.status_code == 200

    client.cookies.set("access_token", response.json()["access_token"])
    client.headers["Authorization"] = f"Bearer {response.json()["access_token"]}"
    client.cookies.set("refresh_token", response.json()["refresh_token"])

    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None

    return client


@pytest.fixture
async def created_user_client(client, user_repository: UserRepository):
    user_create_data = UserCreate(
        email=f"User{random.randint(1, 10000)}@test.com",
        username="user",
        password=make_valid_password(12),
        role=RoleEnum.USER,
        email_verified=True
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
async def created_employee_client(client, user_repository: UserRepository):
    user_create_data = UserCreate(
        email=f"employee_{random.randint(1, 10000)}@test.com",
        username="employee",
        password=make_valid_password(12),
        role=RoleEnum.EMPLOYEE,
        email_verified=True
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
