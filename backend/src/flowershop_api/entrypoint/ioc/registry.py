from typing import Iterable

from dishka import Provider
from dishka.integrations.fastapi import FastapiProvider

from flowershop_api.entrypoint.ioc import (
    AuthProvider,
    DatabaseProvider,
    ServiceProvider,
    RepositoryProvider,
)


def get_providers() -> Iterable[Provider]:
    return (
        AuthProvider(),
        DatabaseProvider(),
        ServiceProvider(),
        RepositoryProvider(),
        FastapiProvider(),
    )
