from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.uow import UnitOfWork
from repositories import (
    IProductRepository,
    ProductRepository,
    ICategoryRepository,
    CategoryRepository,
    IProductImageRepository,
    ProductImageRepository,
    S3Repository,
    IS3Repository,
    OrderRepository,
    IOrderRepository,
    PromocodeRepository,
    IPromocodeRepository,
    UserRepository,
    IUserRepository,
    IPromocodeRepository,
    PromocodeRepository,
)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_product_repository(
        self,
        session: AsyncSession,
    ) -> IProductRepository:
        return ProductRepository(session)

    @provide
    def get_category_repository(
        self,
        session: AsyncSession,
    ) -> ICategoryRepository:
        return CategoryRepository(session)

    @provide
    def get_image_repository(
        self,
        session: AsyncSession,
    ) -> IProductImageRepository:
        return ProductImageRepository(session)

    @provide
    def get_s3_repository(self) -> IS3Repository:
        return S3Repository()

    @provide
    def get_order_repository(self, session: AsyncSession) -> IOrderRepository:
        return OrderRepository(session)

    @provide
    def get_promocode_repository(self, session: AsyncSession) -> IPromocodeRepository:
        return PromocodeRepository(session)

    @provide
    def get_user_repository(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session)

    @provide
    def get_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)
