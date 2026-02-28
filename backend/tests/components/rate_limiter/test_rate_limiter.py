import asyncio

import pytest
from time import time
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_first_request_not_limited(rate_limiter):
    result = await rate_limiter.is_limited(
        identifier="127.0.0.1",
        endpoint="/test",
        windows=[(5, 1)] 
    )
    assert result is False


@pytest.mark.asyncio
async def test_under_limit_not_limited(rate_limiter):
    for _ in range(4):
        await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])
    
    result = await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])
    assert result is False


@pytest.mark.asyncio
async def test_at_limit_is_limited(rate_limiter):
    for _ in range(5):
        await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])

    result = await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])
    assert result is True


@pytest.mark.asyncio
async def test_over_limit_is_limited(rate_limiter):
    for _ in range(10):
        await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])
    
    result = await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])
    assert result is True


@pytest.mark.asyncio
async def test_multiple_windows_all_under_limit(rate_limiter):
    windows = [(5, 1), (20, 60)]
    for _ in range(3):
        await rate_limiter.is_limited("127.0.0.1", "/test", windows)
    
    result = await rate_limiter.is_limited("127.0.0.1", "/test", windows)
    assert result is False


@pytest.mark.asyncio
async def test_multiple_windows_one_exceeded(rate_limiter):
    windows = [(5, 1), (20, 60)]

    for _ in range(6):
        await rate_limiter.is_limited("127.0.0.1", "/test", windows)
    
    result = await rate_limiter.is_limited("127.0.0.1", "/test", windows)
    assert result is True


@pytest.mark.asyncio
async def test_different_identifiers_separate_counters(rate_limiter):
    for _ in range(5):
        await rate_limiter.is_limited("192.168.1.1", "/test", [(5, 1)])

    assert await rate_limiter.is_limited("192.168.1.1", "/test", [(5, 1)]) is True

    for _ in range(5):
        await rate_limiter.is_limited("192.168.1.2", "/test", [(5, 1)])

    assert await rate_limiter.is_limited("192.168.1.2", "/test", [(5, 1)]) is True
    
    assert await rate_limiter.is_limited("192.168.1.3", "/test", [(5, 1)]) is False


@pytest.mark.asyncio
async def test_different_endpoints_separate_counters(rate_limiter):
    for _ in range(5):
        await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])

    assert await rate_limiter.is_limited("127.0.0.1", "/api", [(5, 1)]) is False
    assert await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)]) is True


@pytest.mark.asyncio
async def test_key_format(rate_limiter):
    with patch.object(rate_limiter._redis, 'pipeline') as mock_pipeline:
        mock_pipe = AsyncMock()
        mock_pipeline.return_value.__aenter__.return_value = mock_pipe
        mock_pipe.execute.return_value = [0, 0, 0]  
        
        await rate_limiter.is_limited(
            identifier="127.0.0.1",
            endpoint="/test",
            windows=[(5, 1)]
        )

        mock_pipe.zadd.assert_called_once()
        key = mock_pipe.zadd.call_args[0][0]
        assert key == "rate_limiter:/test:127.0.0.1"


@pytest.mark.asyncio
async def test_window_reset_after_time_passes(rate_limiter):
    windows = [(2, 1)]

    await rate_limiter.is_limited("127.0.0.1", "/test", windows)
    await rate_limiter.is_limited("127.0.0.1", "/test", windows)

    assert await rate_limiter.is_limited("127.0.0.1", "/test", windows) is True

    await asyncio.sleep(1.1)

    result = await rate_limiter.is_limited("127.0.0.1", "/test", windows)
    assert result is False


@pytest.mark.asyncio
async def test_max_window_ttl_set(rate_limiter):
    windows = [(5, 1), (10, 60)]  
    
    with patch.object(rate_limiter._redis, 'pipeline') as mock_pipeline:
        mock_pipe = AsyncMock()
        mock_pipeline.return_value.__aenter__.return_value = mock_pipe
        mock_pipe.execute.return_value = [0, 0, 0, 0]  
        
        await rate_limiter.is_limited("127.0.0.1", "/test", windows)

        mock_pipe.expire.assert_called_once_with(
            "rate_limiter:/test:127.0.0.1", 
            60,
        )


@pytest.mark.asyncio
async def test_unique_request_ids(rate_limiter):
    with patch('core.rate_limiter.rate_limiter.random.randint') as mock_randint:
        mock_randint.return_value = 12345
        
        with patch.object(rate_limiter._redis, 'pipeline') as mock_pipeline:
            mock_pipe = AsyncMock()
            mock_pipeline.return_value.__aenter__.return_value = mock_pipe
            mock_pipe.execute.return_value = [0, 0, 0]
            
            await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])

            called_args = mock_pipe.zadd.call_args[0]
            assert len(called_args) == 2  
            mapping = called_args[1]
            
            request_id = list(mapping.keys())[0]
            assert "--" in request_id
            assert request_id.endswith("--12345")


@pytest.mark.asyncio
async def test_old_requests_cleaned(rate_limiter):
    windows = [(5, 1)]  
    
    with patch.object(rate_limiter._redis, 'pipeline') as mock_pipeline:
        mock_pipe = AsyncMock()
        mock_pipeline.return_value.__aenter__.return_value = mock_pipe
        mock_pipe.execute.return_value = [0, 0, 0]
        
        await rate_limiter.is_limited("127.0.0.1", "/test", windows)

        mock_pipe.zremrangebyscore.assert_called_once()
        args = mock_pipe.zremrangebyscore.call_args[1]
        assert args['min'] == 0


@pytest.mark.asyncio
async def test_empty_windows_list(rate_limiter):
    result = await rate_limiter.is_limited(
        identifier="127.0.0.1",
        endpoint="/test",
        windows=[]  
    )
    assert result is False 


@pytest.mark.asyncio
async def test_redis_error_handling(rate_limiter):
    with patch.object(rate_limiter._redis, 'pipeline') as mock_pipeline:
        mock_pipeline.side_effect = ConnectionError("Redis unavailable")
       
        with pytest.raises(ConnectionError):
            await rate_limiter.is_limited("127.0.0.1", "/test", [(5, 1)])
