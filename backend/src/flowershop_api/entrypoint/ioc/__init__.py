from src.flowershop_api.entrypoint.ioc.auth import AuthProvider
from src.flowershop_api.entrypoint.ioc.database import DatabaseProvider
from src.flowershop_api.entrypoint.ioc.repositories import RepositoryProvider
from src.flowershop_api.entrypoint.ioc.servicies import ServiceProvider

__all__ = [
    "AuthProvider",
    "DatabaseProvider",
    "RepositoryProvider",
    "ServiceProvider",
]
# uvicorn src.run:make_app --factory  --host 0.0.0.0 --port 8000 --reload