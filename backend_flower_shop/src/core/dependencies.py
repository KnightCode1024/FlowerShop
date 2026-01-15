from typing import AsyncGenerator

from dishka import make_async_container, Provider, provide, Scope
from dishka.integrations.fastapi import setup_dishka, FastapiProvider
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker
from repositories.product import ProductRepository
from repositories.category import CategoryRepository
from repositories.product_image import ProductImageRepository
from repositories.s3 import S3Repository
from services.product import ProductsService
from services.category import CategoriesService
from core.uow import UnitOfWork


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_product_repository(
        self,
        session: AsyncSession,
    ) -> ProductRepository:
        return ProductRepository(session)

    @provide
    def get_category_repository(
        self,
        session: AsyncSession,
    ) -> CategoryRepository:
        return CategoryRepository(session)

    @provide
    def get_image_repository(
        self,
        session: AsyncSession,
    ) -> ProductImageRepository:
        return ProductImageRepository(session)

    @provide
    def get_s3_repository(self) -> S3Repository:
        return S3Repository()

    @provide
    def get_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_products_service(
        self,
        uow: UnitOfWork,
    ) -> ProductsService:
        return ProductsService(uow)

    @provide
    def get_categories_service(
        self,
        uow: UnitOfWork,
    ) -> CategoriesService:
        return CategoriesService(uow)


container = make_async_container(
    DatabaseProvider(),
    RepositoryProvider(),
    ServiceProvider(),
    FastapiProvider(),
)


def init_dependencies(app) -> None:
    setup_dishka(container, app)
