from typing import Iterable

from dishka import Provider
from dishka.integrations.fastapi import FastapiProvider

<<<<<<< HEAD
from flowershop_api.entrypoint.ioc import (
    AuthProvider,
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
)
=======
from src.flowershop_api.entrypoint.ioc import (AuthProvider, DatabaseProvider,
                                           RepositoryProvider, ServiceProvider)
>>>>>>> 2aa85980fe433c7c78d7743d6393babc67c1c04b


def get_providers() -> Iterable[Provider]:
    return (
        AuthProvider(),
        DatabaseProvider(),
        ServiceProvider(),
        RepositoryProvider(),
        FastapiProvider(),
    )
