from functools import wraps

from fastapi import HTTPException, status

from models import RoleEnum


def require_roles(allowed_roles: list[RoleEnum]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if user is None:
                raise KeyError("User not found in kwags.")

            if not user or user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have the necessary permissions.",
                )
            return func

        return wrapper

    return decorator
