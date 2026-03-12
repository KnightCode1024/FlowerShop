import inspect
from functools import wraps

from fastapi import HTTPException, status

from models import RoleEnum


def require_roles(allowed_roles: list[RoleEnum]):
    def decorator(func):
        signature = inspect.signature(func)

        def _get_user(args, kwargs):
            if "user" in kwargs:
                return kwargs.get("user")
            if "current_user" in kwargs:
                return kwargs.get("current_user")
            try:
                bound = signature.bind_partial(*args, **kwargs)
                return (
                    bound.arguments.get("user")
                    or bound.arguments.get("current_user")
                )
            except TypeError:
                return None

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                user = _get_user(args, kwargs)
                if user is None:
                    raise KeyError("User not found in kwargs.")

                if not user or user.role not in allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have the necessary permissions.",
                    )
                return await func(*args, **kwargs)

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                user = _get_user(args, kwargs)
                if user is None:
                    raise KeyError("User not found in kwargs.")

                if not user or user.role not in allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have the necessary permissions.",
                    )
                return func(*args, **kwargs)

        return wrapper

    return decorator
