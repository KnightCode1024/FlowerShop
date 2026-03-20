import asyncio
import random

import httpx
import pytest


@pytest.mark.asyncio
async def test_rate_limiter_1_request_in_second_success(client):
    tasks = []

    for i in range(10):
        response1 = await client.get("/ping")
        await asyncio.sleep(3)

        assert response1.status_code != 429, "too many requests"


@pytest.mark.asyncio
async def test_rate_limiter_1_request_in_second_failed(client):
    tasks = []

    response1 = await client.get("/ping")
    response2 = await client.get("/ping")

    assert response2.json()["detail"] == "Too many requests. Please try again later."


@pytest.mark.asyncio
async def test_rate_limiter_2_requests_in_minute_failed(client):
    tasks = []

    response1 = await client.get("/ping")

    await asyncio.sleep(1)

    response2 = await client.get("/ping")

    await asyncio.sleep(1)

    response3 = await client.get("/ping")

    assert response3.json()["detail"] == "Too many requests. Please try again later."


@pytest.mark.asyncio
async def test_rate_limiter_5_requests_in_minute_failed(client):
    tasks = []

    response1 = await client.get("/ping")

    response2 = await client.get("/ping")

    response3 = await client.get("/ping")

    response4 = await client.get("/ping")

    response5 = await client.get("/ping")

    assert response3.json()["detail"] == "Too many requests. Please try again later."
