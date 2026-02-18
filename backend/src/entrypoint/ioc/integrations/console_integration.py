from collections.abc import Callable
from typing import TypeVar

from dishka.integrations.base import wrap_injection

T = TypeVar("T")


def inject(func: Callable) -> Callable:
    return wrap_injection(
        func=func,
        container_getter=lambda args, kwargs: kwargs["dishka_container"],
        manage_scope=True,
        is_async=True,
    )
