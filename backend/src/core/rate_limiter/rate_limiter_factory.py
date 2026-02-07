from functools import wraps

from fastapi import Request, HTTPException, status


def rate_limit(
    endpoint: str,
    max_requests: int,
    window_seconds: int,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            ip_address = request.client.host
            rate_limiter = kwargs.get("rate_limiter")

            if rate_limiter is None:
                raise ValueError("Not rate_limiter.")

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
