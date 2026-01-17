from typing import AsyncGenerator

from dishka import make_async_container, Provider, provide, Scope
from dishka.integrations.fastapi import setup_dishka, FastapiProvider
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker
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


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        session = async_session_maker()
        try:
            yield session
            print("Out session")
        finally:
            await session.close()
            print("Close session")


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


container = make_async_container(
    DatabaseProvider(),
    RepositoryProvider(),
    ServiceProvider(),
    FastapiProvider(),
)


def init_dependencies(app) -> None:
    setup_dishka(container, app)
