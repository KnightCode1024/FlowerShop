import random
import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from entrypoint.ioc.engine import engine
from models import Base, RoleEnum
from repositories import UserRepository
from schemas.user import UserCreate, UserLogin, UserResponse, UserCreateConsole
from utils.strings import generate_random_token


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="session")
async def clear_db():
    async with engine.begin() as conn:
        tables = ", ".join(
            f'"{t.schema}"."{t.name}"' if t.schema else f'"{t.name}"'
            for t in Base.metadata.sorted_tables
        )
        if tables:
            await conn.exec_driver_sql(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE;")
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


@pytest.fixture
async def session(async_session_maker):
    async with async_session_maker() as session:
        yield session

        await session.rollback()


@pytest.fixture
async def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session=session)


@pytest.fixture
async def created_admin_client(client, user_repository):
    user_create_data = UserCreateConsole(
        email=f"ADMINadminov{random.randint(1, 10000)}@test.com",
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
    client.cookies.set("refresh_token", response.json()["access_token"])

    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None

    return client


@pytest.fixture
async def created_user_client(client, user_repository):
    user_create_data = UserCreateConsole(
        email=f"User{random.randint(1, 10000)}@test.com",
        username="user",
        password=generate_random_token(10) + "@",
        role=RoleEnum.USER,
    )
    user = await user_repository.create(user_create_data)

    assert user_create_data.email == user.email

    login_data = UserLogin(email=user_create_data.email, password=user_create_data.password)
    response = await client.post("/users/login", json=login_data.model_dump())

    assert response.status_code == 200

    client.cookies.set("access_token", response.json()["access_token"])
    client.headers["Authorization"] = f"Bearer {response.json()["access_token"]}"
    client.cookies.set("refresh_token", response.json()["access_token"])

    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None

    return client
