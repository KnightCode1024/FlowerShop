from dishka import Provider, Scope, provide

from core.uow import UnitOfWork
from repositories import (
    ICategoryRepository,
    IInvoiceRepository,
    IOrderRepository,
    IProductImageRepository,
    IProductRepository,
    IPromocodeRepository,
    IS3Repository,
    IUserRepository,
)
from services import (
    CategoryService,
    OrderService,
    ProductService,
    UserService,
    PromocodeService,
    InvoiceService,
)
from entrypoint.ioc.providers.dependencies import factories


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_products_service(
            self,
            uow: UnitOfWork,
            product_repository: IProductRepository,
            category_repository: ICategoryRepository,
            image_repository: IProductImageRepository,
            s3_repository: IS3Repository,
    ) -> ProductService:
        return ProductService(
            uow,
            product_repository,
            category_repository,
            image_repository,
            s3_repository,
        )

    @provide
    def get_invoices_service(
            self,
            uow: UnitOfWork,
            invoice_repository: IInvoiceRepository,
            orders_repository: IOrderRepository,
            products_repository: IProductRepository,
            user_repository: IUserRepository,
    ) -> InvoiceService:
        return InvoiceService(uow,
                              products_repository,
                              invoice_repository,
                              orders_repository,
                              user_repository,
                              factories)

    @provide
    def get_categories_service(
            self,
            uow: UnitOfWork,
            category_repository: ICategoryRepository,
    ) -> CategoryService:
        return CategoryService(uow, category_repository)

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
            order_repository: IOrderRepository,
            product_repository: IProductRepository,
    ) -> OrderService:
        return OrderService(uow, order_repository, product_repository)

    @provide
    def get_promocode_service(
            self,
            uow: UnitOfWork,
            promocode_repository: IPromocodeRepository,
    ) -> PromocodeService:
        return PromocodeService(uow, promocode_repository)
