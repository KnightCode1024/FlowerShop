import random
import httpx
import pytest
import pytest_asyncio

from entrypoint.ioc.engine import engine
from models import Base
from schemas.user import UserCreate, UserLogin, UserResponse


@pytest_asyncio.fixture(loop_scope="session")
async def clear_db():
    tables = ", ".join(
        f'{t.schema + "." if t.schema else ""}"{t.name}"'
        for t in Base.metadata.sorted_tables
    )

    if tables:
        query = f'TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE;'
        async with engine.begin() as conn:
            await conn.exec_driver_sql(query)

    return True


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
