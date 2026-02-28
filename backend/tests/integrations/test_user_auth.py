import pytest
from httpx import AsyncClient

from models import User
from schemas.user import UserLogin, UserCreate, UserResponse
import random

from utils.strings import generate_random_password, make_valid_password


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    login_data = UserLogin(email=f"test{random.randint(10000, 99999999)}@test.com", password=make_valid_password(16))

    response = await client.post("/users/login", json=login_data.model_dump())

    assert response.status_code == 401
    assert response.json()["detail"] == "Uncorrect login or password"


@pytest.mark.asyncio
async def test_login_user_success(created_user_client, client):
    resp = await created_user_client.get("/users/me")
    user_me = UserResponse(**resp.json())

    assert user_me


@pytest.mark.asyncio
async def test_register_user_not_verified(client):
    register_data = UserCreate(email=f"test1@test.com", password=make_valid_password(), username="Alex")
    created_user = await client.post("/users/register", json=register_data.model_dump())

    assert created_user.status_code == 400
    assert created_user.json()["detail"] == "Email already exists"
