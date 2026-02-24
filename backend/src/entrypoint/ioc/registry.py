from collections.abc import Iterable

from dishka import Provider
from dishka.integrations.fastapi import FastapiProvider

from entrypoint.ioc import (AuthProvider, ConfigProvider, DatabaseProvider,
                            RateLimiterProvider, RedisProvider,
                            RepositoryProvider, ServiceProvider)


def get_providers() -> Iterable[Provider]:
    return (
        DatabaseProvider(),
        AuthProvider(),
        ServiceProvider(),
        RepositoryProvider(),
        FastapiProvider(),
        ConfigProvider(),
        RedisProvider(),
        RateLimiterProvider(),
    )
