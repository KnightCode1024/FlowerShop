from typing import Iterable

from dishka import Provider
from dishka.integrations.fastapi import FastapiProvider

from src.flowershop_api.entrypoint.ioc import (
    AuthProvider,
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
)
from src.flowershop_api.entrypoint.ioc import (AuthProvider, DatabaseProvider,
                                           RepositoryProvider, ServiceProvider)


def get_providers() -> Iterable[Provider]:
    return (
        AuthProvider(),
        DatabaseProvider(),
        ServiceProvider(),
        RepositoryProvider(),
        FastapiProvider(),
    )
