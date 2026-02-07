from typing import Iterable

from dishka import Provider
from dishka.integrations.fastapi import FastapiProvider


from entrypoint.ioc import (
    AuthProvider,
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
    ConfigProvider,
    RateLimiterProvider,
    RedisProvider,
)


def get_providers() -> Iterable[Provider]:
    return (
        AuthProvider(),
        DatabaseProvider(),
        ServiceProvider(),
        RepositoryProvider(),
        FastapiProvider(),
        ConfigProvider(),
        RedisProvider(),
        RateLimiterProvider(),
    )
