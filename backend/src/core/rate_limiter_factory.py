from functools import lru_cache, wraps
from typing import Annotated

from fastapi import Request, Depends, HTTPException, status
from redis.asyncio import Redis

from core.rate_limiter import RateLimiter

from entrypoint.config import config


@lru_cache
def get_redis() -> Redis:
    return Redis(
        host=config.redis.HOST,
        port=config.redis.PORT,
    )


@lru_cache
def get_rate_limiter():
    return RateLimiter(get_redis())


def rate_limit(
    endpoint: str,
    max_requests: int,
    window_seconds: int,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # request = None

            # for arg in args:
            #     if isinstance(arg, Request):
            #         request = arg
            #         break

            # for kwarg in kwargs.values():
            #     if isinstance(kwarg, Request):
            #         request = kwarg
            #         break

            # if request is None:
            #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            ip_address = request.client.host
            rate_limiter = get_rate_limiter()

            limited = await rate_limiter.is_limited(
                ip_address,
                endpoint,
                max_requests,
                window_seconds,
            )
            if limited:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Exceeded max requests. Try later.",
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
