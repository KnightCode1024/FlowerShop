import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import Request
from src.core.rate_limiter import rate_limit
from src.core.rate_limiter.strategy import Strategy


@pytest.mark.asyncio
async def test_rate_limit_ip_strategy_allowed():
    mock_request = Mock(spec=Request)
    
    mock_client = Mock()
    mock_client.host = "127.0.0.1"
    mock_request.client = mock_client

    mock_request.headers = {}
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_limited.return_value = False
    
    @rate_limit(strategy=Strategy.IP, policy="5/s;10/m")
    async def test_endpoint(request, rate_limiter, current_user=None):
        return {"status": "success"}
    
    result = await test_endpoint(
        request=mock_request,
        rate_limiter=mock_rate_limiter,
        current_user=None
    )
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once_with(
        "127.0.0.1",
        "/test-endpoint",
        [(5, 1), (10, 60)]
    )