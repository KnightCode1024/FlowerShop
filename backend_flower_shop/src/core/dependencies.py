from typing import AsyncGenerator

from dishka import make_async_container, Provider, provide, Scope
from dishka.integrations.fastapi import setup_dishka, FastapiProvider
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker
from core.config import AppConfig, config, S3Config, DatabaseConfig
from core.s3_client import S3Client
from repositories.product import ProductRepository
from repositories.category import CategoryRepository
from repositories.product_image import ProductImageRepository
from repositories.s3 import S3Repository
from repositories.interfaces import (
    ProductRepositoryInterface,
    CategoryRepositoryInterface,
    ProductImageRepositoryInterface,
    S3RepositoryInterface,
)
from services.product import ProductsService
from services.category import CategoriesService
from core.uow import UnitOfWork


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> AppConfig:
        return config

    @provide(scope=Scope.APP)
    def get_s3_config(self) -> S3Config:
        return config.s3

    @provide(scope=Scope.APP)
    def get_database_config(self) -> DatabaseConfig:
        return config.database


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        session = async_session_maker()
        try:
            yield session
        finally:
            await session.close()


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_product_repository(
        self,
        session: AsyncSession,
    ) -> ProductRepositoryInterface:
        return ProductRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_category_repository(
        self,
        session: AsyncSession,
    ) -> CategoryRepositoryInterface:
        return CategoryRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_image_repository(
        self,
        session: AsyncSession,
    ) -> ProductImageRepositoryInterface:
        return ProductImageRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_s3_repository(self) -> S3RepositoryInterface:
        return S3Repository()

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_products_service(
        self,
        uow: UnitOfWork,
        product_repository: ProductRepositoryInterface,
        category_repository: CategoryRepositoryInterface,
        image_repository: ProductImageRepositoryInterface,
        s3_repository: S3RepositoryInterface,
    ) -> ProductsService:
        return ProductsService(
            uow,
            product_repository,
            category_repository,
            image_repository,
            s3_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_categories_service(
        self,
        uow: UnitOfWork,
        category_repository: CategoryRepositoryInterface,
    ) -> CategoriesService:
        return CategoriesService(uow, category_repository)


class ClientProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_s3_client() -> S3Client:
        return S3Client()


container = make_async_container(
    DatabaseProvider(),
    RepositoryProvider(),
    ServiceProvider(),
    FastapiProvider(),
    ConfigProvider(),
)


def init_dependencies(app) -> None:
    setup_dishka(container, app)
