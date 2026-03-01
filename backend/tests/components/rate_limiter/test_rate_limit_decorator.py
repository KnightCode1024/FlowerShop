import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import Request, HTTPException
from core.rate_limiter import rate_limit
from core.rate_limiter.strategy import Strategy


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


@pytest.mark.asyncio
async def test_rate_limit_ip_strategy_with_x_forwarded_for():
    mock_request = Mock(spec=Request)
    
    mock_request.client = None
    mock_request.headers = {"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_limited.return_value = False
    
    @rate_limit(strategy=Strategy.IP, policy="5/s")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    result = await test_endpoint(
        request=mock_request,
        rate_limiter=mock_rate_limiter
    )
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once_with(
        "203.0.113.1",
        "/test-endpoint",
        [(5, 1)]
    )


@pytest.mark.asyncio
async def test_rate_limit_ip_strategy_unknown_client():
    mock_request = Mock(spec=Request)
    
    mock_request.client = None
    mock_request.headers = {}
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_limited.return_value = False
    
    @rate_limit(strategy=Strategy.IP, policy="5/s")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    result = await test_endpoint(
        request=mock_request,
        rate_limiter=mock_rate_limiter
    )
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once_with(
        "unknown",
        "/test-endpoint",
        [(5, 1)]
    )


@pytest.mark.asyncio
async def test_rate_limit_user_strategy_with_kwarg_user():
    mock_request = Mock(spec=Request)
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_limited.return_value = False
    
    mock_user = Mock()
    mock_user.id = 123
    
    @rate_limit(strategy=Strategy.USER, policy="10/m")
    async def test_endpoint(request, rate_limiter, current_user):
        return {"status": "success"}
    
    result = await test_endpoint(
        request=mock_request,
        rate_limiter=mock_rate_limiter,
        current_user=mock_user
    )
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once_with(
        "123",
        "/test-endpoint",
        [(10, 60)]
    )


@pytest.mark.asyncio
async def test_rate_limit_user_strategy_with_request_state_user():
    mock_request = Mock(spec=Request)
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_state = Mock()
    mock_state.user = Mock()
    mock_state.user.id = 456
    mock_request.state = mock_state
    
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_limited.return_value = False
    
    @rate_limit(strategy=Strategy.USER, policy="10/m")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    result = await test_endpoint(
        request=mock_request,
        rate_limiter=mock_rate_limiter
    )
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once_with(
        "456",
        "/test-endpoint",
        [(10, 60)]
    )


@pytest.mark.asyncio
async def test_rate_limit_user_strategy_with_header():
    mock_request = Mock(spec=Request)
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_request.state = Mock()
    mock_request.state.user = None
    
    mock_request.headers = {"X-User-Id": "789"}
    
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_limited.return_value = False
    
    @rate_limit(strategy=Strategy.USER, policy="10/m")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    result = await test_endpoint(
        request=mock_request,
        rate_limiter=mock_rate_limiter
    )
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once_with(
        "789",
        "/test-endpoint",
        [(10, 60)]
    )


@pytest.mark.asyncio
async def test_rate_limit_user_strategy_unauthorized():
    mock_request = Mock(spec=Request)
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_request.state = Mock()
    mock_request.state.user = None
    mock_request.headers = {}
    
    mock_rate_limiter = AsyncMock()
    
    @rate_limit(strategy=Strategy.USER, policy="10/m")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    with pytest.raises(HTTPException) as exc_info:
        await test_endpoint(
            request=mock_request,
            rate_limiter=mock_rate_limiter
        )
    
    assert exc_info.value.status_code == 401
    assert "User not authenticated" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_rate_limit_find_rate_limiter_in_args():
    mock_request = Mock(spec=Request)
    
    mock_client = Mock()
    mock_client.host = "127.0.0.1"
    mock_request.client = mock_client
    mock_request.headers = {}
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_limited = AsyncMock(return_value=False)
    
    @rate_limit(strategy=Strategy.IP, policy="5/s")
    async def test_endpoint(request, limiter):  
        return {"status": "success"}

    result = await test_endpoint(mock_request, mock_rate_limiter)
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limit_no_request_found():
    mock_rate_limiter = AsyncMock()
    
    @rate_limit(strategy=Strategy.IP, policy="5/s")
    async def test_endpoint(some_arg):
        return {"status": "success"}
    
    with pytest.raises(HTTPException) as exc_info:
        await test_endpoint(some_arg=mock_rate_limiter)
    
    assert exc_info.value.status_code == 400
    assert "Request object not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_rate_limit_no_rate_limiter_found():
    mock_request = Mock(spec=Request)
    
    mock_client = Mock()
    mock_client.host = "127.0.0.1"
    mock_request.client = mock_client
    mock_request.headers = {}
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    @rate_limit(strategy=Strategy.IP, policy="5/s")
    async def test_endpoint(request):
        return {"status": "success"}
    
    with pytest.raises(ValueError) as exc_info:
        await test_endpoint(request=mock_request)
    
    assert "Rate limiter not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_rate_limit_invalid_policy_format():
    mock_request = Mock(spec=Request)
    mock_rate_limiter = AsyncMock()
    
    @rate_limit(strategy=Strategy.IP, policy="invalid_policy")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    with pytest.raises(ValueError) as exc_info:
        await test_endpoint(
            request=mock_request,
            rate_limiter=mock_rate_limiter
        )

    error_msg = str(exc_info.value)
    assert "Invalid request policy" in error_msg


@pytest.mark.asyncio
async def test_rate_limit_invalid_policy_segment():
    mock_request = Mock(spec=Request)
    mock_rate_limiter = AsyncMock()
    
    @rate_limit(strategy=Strategy.IP, policy="5/x;10/m")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    with pytest.raises(ValueError) as exc_info:
        await test_endpoint(
            request=mock_request,
            rate_limiter=mock_rate_limiter
        )

    error_msg = str(exc_info.value)
    assert "Invalid request policy" in error_msg


@pytest.mark.asyncio
async def test_rate_limit_too_many_requests():
    mock_request = Mock(spec=Request)
    
    mock_client = Mock()
    mock_client.host = "127.0.0.1"
    mock_request.client = mock_client
    mock_request.headers = {}
    
    mock_url = Mock()
    mock_url.path = "/test-endpoint"
    mock_request.url = mock_url
    
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_limited.return_value = True
    
    @rate_limit(strategy=Strategy.IP, policy="5/s")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    with pytest.raises(HTTPException) as exc_info:
        await test_endpoint(
            request=mock_request,
            rate_limiter=mock_rate_limiter
        )
    
    assert exc_info.value.status_code == 429
    assert "Too many requests" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_rate_limit_max_three_segments():
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
    
    @rate_limit(strategy=Strategy.IP, policy="5/s;10/m;20/h")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    result = await test_endpoint(
        request=mock_request,
        rate_limiter=mock_rate_limiter
    )
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once_with(
        "127.0.0.1",
        "/test-endpoint",
        [(5, 1), (10, 60), (20, 3600)]
    )


@pytest.mark.asyncio
async def test_rate_limit_policy_with_more_than_three_segments():
    mock_request = Mock(spec=Request)
    mock_rate_limiter = AsyncMock()
    
    @rate_limit(strategy=Strategy.IP, policy="5/s;10/m;20/h;30/d")
    async def test_endpoint(request, rate_limiter):
        return {"status": "success"}
    
    with pytest.raises(ValueError) as exc_info:
        await test_endpoint(
            request=mock_request,
            rate_limiter=mock_rate_limiter
        )
    
    assert "Invalid request policy" in str(exc_info.value)


@pytest.mark.asyncio
async def test_rate_limit_request_in_args():
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
    
    @rate_limit(strategy=Strategy.IP, policy="5/s")
    async def test_endpoint(some_arg, another_arg):
        return {"status": "success"}
    
    result = await test_endpoint(
        mock_request,
        mock_rate_limiter
    )
    
    assert result == {"status": "success"}
    mock_rate_limiter.is_limited.assert_called_once()
