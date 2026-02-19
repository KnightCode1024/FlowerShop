import asyncio
import random

import httpx
import pytest


@pytest.mark.asyncio
async def test_all_routers(client):
    tasks = []

    for i in range(5):
        tasks.append(client.get("/ping"))
        tasks.append(client.post("/orders/"))
        tasks.append(client.post("/products/"))
        tasks.append(client.post("/promocodes/"))
        tasks.append(client.post("/users/"))

    await asyncio.gather(*tasks)
