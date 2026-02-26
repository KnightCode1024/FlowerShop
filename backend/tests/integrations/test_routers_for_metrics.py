import asyncio
import random

import httpx
import pytest


@pytest.mark.asyncio
async def test_all_routers(client):
    tasks = []

    for i in range(5):
        tasks.append(client.get("/ping"))

    await asyncio.gather(*tasks)
