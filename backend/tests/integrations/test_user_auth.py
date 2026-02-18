import pytest
from httpx import AsyncClient

from models import User
from schemas.user import UserLogin, UserCreate, UserResponse
import random


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    login_data = UserLogin(email=f"test{random.randint(10000, 99999999)}@test.com", password="12345678")

    response = await client.post("/users/login", json=login_data.model_dump())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_user_success(user_factory, client):
    user = await user_factory()

    resp = await client.get("/users/me")
    user_me = UserResponse(**resp.json())

    assert user.id == user_me.id
    assert user.email == user_me.email


@pytest.mark.asyncio
async def test_register_user_already_exists(clear_db, user_factory, client):
    register_data = UserCreate(email=f"test1@test.com", password="12345678A@", username="Alex")

    created_user = await client.post("/users/register", json=register_data.model_dump())

    assert created_user.status_code == 200
    assert created_user.json()["email"] == register_data.email

    register_data = UserCreate(email=f"test1@test.com", password="12345678A@", username="Alex")

    created_user2 = await client.post("/users/register", json=register_data.model_dump())

    assert created_user2.status_code == 400
    assert created_user2.json()["detail"] == "Email already exists"

