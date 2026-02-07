from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.uow import UnitOfWork
from repositories import (
    CategoryRepository,
    CategoryRepositoryI,
    ProductImageRepository,
    ProductImageRepositoryI,
    ProductRepository,
    ProductRepositoryI,
    S3Repository,
    S3RepositoryI,
    UserRepository,
    UserRepositoryI,
)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_product_repository(
        self,
        session: AsyncSession,
    ) -> ProductRepositoryI:
        return ProductRepository(session)

    @provide
    def get_category_repository(
        self,
        session: AsyncSession,
    ) -> CategoryRepositoryI:
        return CategoryRepository(session)

    @provide
    def get_image_repository(
        self,
        session: AsyncSession,
    ) -> ProductImageRepositoryI:
        return ProductImageRepository(session)

    @provide
    def get_s3_repository(self) -> S3RepositoryI:
        return S3Repository()

    @provide
    def get_user_repository(self, session: AsyncSession) -> UserRepositoryI:
        return UserRepository(session)

    @provide
    def get_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)
