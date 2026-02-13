from dishka import Provider, Scope, provide

from core.uow import UnitOfWork
from repositories import (
    ICategoryRepository,
    IProductImageRepository,
    IProductRepository,
    S3RepositoryI,
    IUserRepository,
    IOrderRepository, IPromocodeRepository
)
from services import CategoriesService, ProductsService, UserService, OrdersService
from services.promocode import PromocodesService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_products_service(
            self,
            uow: UnitOfWork,
            product_repository: IProductRepository,
            category_repository: ICategoryRepository,
            image_repository: IProductImageRepository,
            s3_repository: S3RepositoryI,
    ) -> ProductsService:
        return ProductsService(
            uow,
            product_repository,
            category_repository,
            image_repository,
            s3_repository,
        )

    @provide
    def get_categories_service(
            self,
            uow: UnitOfWork,
            category_repository: ICategoryRepository,
    ) -> CategoriesService:
        return CategoriesService(uow, category_repository)

    @provide
    def get_user_service(
            self,
            uow: UnitOfWork,
            user_repository: IUserRepository,
    ) -> UserService:
        return UserService(uow, user_repository)

    @provide
    def get_order_service(
            self,
            uow: UnitOfWork,
            order_repository: IOrderRepository
    ) -> OrdersService:
        return OrdersService(uow, order_repository)

    @provide
    def get_promocode_service(self,
                              uow: UnitOfWork,
                              promocode_repository: IPromocodeRepository) -> PromocodesService:
        return PromocodesService(uow, promocode_repository)
