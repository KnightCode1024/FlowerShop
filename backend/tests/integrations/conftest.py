import random

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text

from entrypoint.ioc import DatabaseProvider
from models import Base
from schemas.user import UserCreate, UserLogin, UserResponse


@pytest_asyncio.fixture(loop_scope="session")
async def clear_db():
    async with DatabaseProvider().engine.begin() as conn:
        tables = ", ".join(Base.metadata.tables.values())
        query = f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE;"
        await conn.execute(text(query))

    return True


@pytest.fixture
async def client(base_url="http://localhost:8000/api"):
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
        print(client.headers)

        client.cookies.set("access_token", response2.json()["access_token"])
        client.headers["Authorization"] = f"Bearer {response2.json()["access_token"]}"
        client.cookies.set("refresh_token", response2.json()["access_token"])

        assert response2.json()["access_token"] is not None
        assert response2.json()["refresh_token"] is not None

        return UserResponse(**created_user.json())

    return _create
