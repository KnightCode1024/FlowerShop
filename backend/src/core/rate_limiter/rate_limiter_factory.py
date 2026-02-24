import re
from functools import wraps

from fastapi import HTTPException, Request, status

from core.rate_limiter.strategy import Strategy


def rate_limit(strategy: Strategy = Strategy.IP, policy: str | None = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None

            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
     
            if request is None:
                request = kwargs.get("request")
     
            if request is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request object not found",
                )

            if not policy or not re.match(
                r"^(\d+\/[smhd])(;\d+\/[smhd]){0,2}$", 
                policy,
            ):
                raise ValueError(
                    f"Invalid request policy: {policy}.", 
                    "Expected format: '5/s', '10/m', '20/h', '30/d'",
                    )

            request_policy = policy.split(";")

            identifier = None
            if strategy == Strategy.IP:
                forwarded = request.headers.get("X-Forwarded-For")
                if forwarded:
                    identifier = forwarded.split(",")[0].strip()
                else:
                    identifier = request.client.host if request.client else "unknown"

            elif strategy == Strategy.USER:
                user = kwargs.get("current_user") or kwargs.get("user")
                if user is not None and hasattr(user, "id"):
                    identifier = str(user.id)
                else:
                    state_user = getattr(request.state, "user", None)
                    if state_user is not None and hasattr(state_user, "id"):
                        identifier = str(state_user.id)
                    else:
                        identifier = request.headers.get("X-User-Id")

                if identifier is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=(
                            "User not authenticated ",
                            "for USER rate-limiting strategy.",
                        )
                    )

            if identifier is None:
                identifier = "unknown"

            rate_limiter = kwargs.get("rate_limiter")
            if rate_limiter is None:
                for arg in args:
                    if hasattr(arg, 'is_limited'): 
                        rate_limiter = arg
                        break

            if rate_limiter is None:
                raise ValueError("Rate limiter not found in arguments")

            endpoint = request.url.path

            windows = []
            for rp in request_policy:
                m = re.match(r"^(\d+)\/([smhd])$", rp)
                if not m:
                    raise ValueError(
                        f"Invalid policy segment: {rp}.",
                        "Expected format like '5/s', '10/m', '20/h', '30/d'",
                        )

                max_requests = int(m.group(1))
                unit = m.group(2)

                if unit == "s":
                    window_seconds = 1
                elif unit == "m":
                    window_seconds = 60
                elif unit == "h":
                    window_seconds = 60 * 60
                else: 
                    window_seconds = 24 * 60 * 60

                windows.append((max_requests, window_seconds))

            limited = await rate_limiter.is_limited(
                identifier,
                endpoint,
                windows,
            )
            if limited:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
