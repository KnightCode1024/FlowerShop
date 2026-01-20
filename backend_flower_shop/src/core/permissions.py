from functools import wraps
from typing import Callable, Any

from models import RoleEnum
from schemas.user import UserResponse, AnonymousUserResponse

from fastapi import HTTPException, status


def require_roles(allowed_roles: list[RoleEnum]):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(current_user: UserResponse) -> Callable:
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Unprocessable user entity",
                )
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have sufficient access rights",
                )

            return await func(current_user)

        return wrapper

    return decorator
