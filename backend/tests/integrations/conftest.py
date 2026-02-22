import asyncio
import os
import random
from decimal import Decimal

import httpx
import pytest
import pytest_asyncio
from dishka import FromDishka
from sqlalchemy import event, StaticPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from entrypoint.ioc.engine import session_factory
from core.uow import UnitOfWork
from entrypoint.ioc.engine import engine
from models import Base, RoleEnum
from repositories import UserRepository, ProductRepository, CategoryRepository
from schemas.category import CategoryCreate
from schemas.product import ProductCreate
from schemas.user import UserCreate, UserLogin, UserResponse, UserCreateConsole
from services import UserService
from utils.strings import generate_random_token, generate_random_password, make_valid_password


@pytest.fixture
async def session() -> AsyncSession:
    async with session_factory() as s:
        yield s


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
async def user_repository(session):
    return UserRepository(session=session)


async def test_category_for_products(category_repository: CategoryRepository):
    category_data = CategoryCreate(name="Flowers")
    return await category_repository.create(category_data)


@pytest.fixture
async def category_repository(session: AsyncSession):
    return CategoryRepository(session=session)


@pytest.fixture
async def product_repository(session):
    return ProductRepository(session=session)


@pytest.fixture
async def created_product(product_repository, test_product1):
    return await product_repository.create(test_product1)


@pytest.fixture
async def user_service(user_repository, session: AsyncSession) -> UserService:
    assert isinstance(session, AsyncSession), f"ожидался AsyncSession, получили {type(session)}"

    return UserService(UnitOfWork(session), user_repository)


@pytest.fixture
async def created_admin_client(client, user_service: UserService):
    user_create_data = UserCreateConsole(
        email=f"ADMIN_adminov{random.randint(1, 10000)}@test.com",
        username="admin",
        password=make_valid_password(12),
        role=RoleEnum.ADMIN,
    )
    user = await user_service.create_user_for_console(user_create_data)

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
async def created_user_client(client, user_service: UserService):
    user_create_data = UserCreateConsole(
        email=f"User{random.randint(1, 10000)}@test.com",
        username="user",
        password=make_valid_password(12),
        role=RoleEnum.USER
    )
    user = await user_service.create_user_for_console(user_create_data)

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
