import asyncio
import random

import pytest


@pytest.mark.asyncio
async def test_all_routers(client):
    tasks = []

    for i in range(random.randint(1000, 10000)):
        tasks.append(await client.get("/ping"))
        tasks.append(await client.post("/orders/"))
        tasks.append(await client.post("/products/"))
        tasks.append(await client.post("/promocodes/"))
        tasks.append(await client.post("/users/"))

    await asyncio.gather(*tasks)
