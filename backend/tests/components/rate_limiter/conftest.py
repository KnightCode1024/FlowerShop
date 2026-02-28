import pytest
from unittest.mock import patch
from src.core.rate_limiter.rate_limiter import RateLimiter
from tests.mocks.redis import MockRedis
from fastapi import Request

@pytest.fixture
async def rate_limiter():
    mock_redis = MockRedis()
    limiter = RateLimiter(mock_redis)
    return limiter


# @pytest.fixture
# async def rate_limiter_with_patch():
#     mock_redis = MockRedis()

#     with patch(
#         'core.rate_limiter.rate_limiter.Redis',
#         return_value=mock_redis,
#     ):
#         limiter = RateLimiter(mock_redis)
#         yield limiter

def request(
    path: str = "/test",
    headers: dict | None = None,
    client_host: str = "127.0.0.1",
):
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [
            (k.lower().encode(), v.encode())
            for k, v in (headers or {}).items()
        ],
        "client": (client_host, 12345),
    }
    return Request(scope)
