import httpx
import pytest


@pytest.fixture
async def client(base_url="http://backend:8000/api"):
    async with httpx.AsyncClient(base_url=base_url) as client:
        yield client
