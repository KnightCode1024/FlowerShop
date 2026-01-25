from dishka import Provider, provide, Scope

from app.repositories import (
    ProductRepositoryI,
    CategoryRepositoryI,
    ProductImageRepositoryI,
    S3RepositoryI,
    UserRepositoryI,
)
from app.services import (
    ProductsService,
    CategoriesService,
    UserService,
)
from app.core.uow import UnitOfWork


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_products_service(
        self,
        uow: UnitOfWork,
        product_repository: ProductRepositoryI,
        category_repository: CategoryRepositoryI,
        image_repository: ProductImageRepositoryI,
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
        category_repository: CategoryRepositoryI,
    ) -> CategoriesService:
        return CategoriesService(uow, category_repository)

    @provide
    def get_user_service(
        self,
        uow: UnitOfWork,
        user_repository: UserRepositoryI,
    ) -> UserService:
        return UserService(uow, user_repository)
