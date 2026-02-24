from dishka import Provider, Scope, provide

from core.uow import UnitOfWork
<<<<<<< HEAD
from entrypoint.config import Config
from interfaces import IEmailService
from repositories import (ICategoryRepository, IOrderRepository,
                          IProductImageRepository, IProductRepository,
                          IPromocodeRepository, IS3Repository, IUserRepository)
from services import (CategoryService, EmailService, OrderService,
                      ProductService, UserService)
from services.promocode import PromocodeService
=======
from providers import IPaymentProvider
from providers.dependencies import yoomoney_factory
from repositories import (
    ICategoryRepository,
    IProductImageRepository,
    IProductRepository,
    S3RepositoryI,
    IUserRepository,
    IOrderRepository, IPromocodeRepository
)
from repositories.invoice import InvoiceRepositoryI
from schemas.invoice import Methods
from services import CategoriesService, ProductsService, UserService, OrdersService
from services.invoice import InvoiceService
from services.promocode import PromocodesService
>>>>>>> origin/main


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
    def get_invoices_service(self,
                             uow: UnitOfWork,
                             invoice_repository: InvoiceRepositoryI) -> InvoiceService:
        return InvoiceService(uow, invoice_repository,
                              {
                                  Methods.YOOMONEY: yoomoney_factory
                              })

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
        email_service: IEmailService,
    ) -> UserService:
        return UserService(uow, user_repository, email_service)

    @provide
    def get_email_service(self, config: Config) -> IEmailService:
        return EmailService(config)

    @provide
    def get_order_service(
        self, uow: UnitOfWork, order_repository: IOrderRepository
    ) -> OrderService:
        return OrderService(uow, order_repository)

    @provide
    def get_promocode_service(
        self,
        uow: UnitOfWork,
        promocode_repository: IPromocodeRepository,
    ) -> PromocodeService:
        return PromocodeService(uow, promocode_repository)
