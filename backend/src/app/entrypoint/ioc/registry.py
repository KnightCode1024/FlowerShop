from typing import Iterable

from dishka import Provider
from dishka.integrations.fastapi import FastapiProvider

from app.entrypoint.ioc import (
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
