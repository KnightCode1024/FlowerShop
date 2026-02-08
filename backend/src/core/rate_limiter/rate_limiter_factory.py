import re
from functools import wraps

from fastapi import Request, HTTPException, status


from core.rate_limiter.strategy import Strategy


def rate_limit(strategy: Strategy = Strategy.IP, policy: str | None = None):
    """
    Usage:
      @rate_limit(strategy=Strategy.IP, policy="10/s;100/m;500/h")
    The decorator expects the endpoint handler to accept a `rate_limiter`
    dependency (e.g. `rate_limiter: FromDishka[RateLimiter]`) so it can call
    `is_limited(...)`.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not policy or not re.match(
                r"^(\d+\/[smh])(;\d+\/[smh]){0,2}$",
                policy,
            ):
                raise ValueError("Invalid request policy.")

            request_policy = policy.split(";")

            identifier = None
            if strategy == Strategy.IP:
                identifier = request.client.host
            elif strategy == Strategy.USER:
                user = kwargs.get("current_user") or kwargs.get(
                    "user",
                )
                if user is not None and hasattr(user, "id"):
                    identifier = getattr(user, "id")
                else:
                    state_user = getattr(request.state, "user", None)
                    if state_user is not None and hasattr(state_user, "id"):
                        identifier = getattr(state_user, "id")
                    else:
                        identifier = request.headers.get("X-User-Id")
                if identifier is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=(
                            "User not authenticated for USER",
                            " rate-limiting strategy.",
                        ),
                    )

            rate_limiter = kwargs.get("rate_limiter")
            if rate_limiter is None:
                raise ValueError("Not rate_limiter.")

            endpoint = getattr(request.url, "path", None) or request.url.path

            windows = []
            for rp in request_policy:
                m = re.match(r"^(\d+)\/([smh])$", rp)
                if not m:
                    raise ValueError("Invalid policy segment.")

                max_requests = int(m.group(1))
                unit = m.group(2)
                if unit == "s":
                    window_seconds = 1
                elif unit == "m":
                    window_seconds = 60
                else:
                    window_seconds = 3600

                windows.append((max_requests, window_seconds))

            limited = await rate_limiter.is_limited(
                identifier,
                endpoint,
                windows,
            )
            if limited:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Exceeded max requests. Try later.",
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
