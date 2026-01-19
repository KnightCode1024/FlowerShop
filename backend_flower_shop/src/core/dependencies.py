from typing import AsyncGenerator

from dishka import make_async_container, Provider, provide, Scope
from dishka.integrations.fastapi import setup_dishka, FastapiProvider
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer
from fastapi import Request, status, HTTPException

from core.database import async_session_maker
from core.config import AppConfig, config, S3Config, DatabaseConfig
from core.s3_client import S3Client
from repositories import (
    ProductRepository,
    CategoryRepository,
    ProductRepositoryI,
    CategoryRepositoryI,
    ProductImageRepositoryI,
    S3RepositoryI,
    ProductImageRepository,
    S3Repository,
    UserRepository,
    UserRepositoryI,
)
from services import ProductsService, CategoriesService, UserService
from core.uow import UnitOfWork
from schemas.user import UserResponse
from utils.jwt import decode_jwt

security = HTTPBearer()


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


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self,
        user_service: UserService,
        request: Request,
    ) -> UserResponse:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
            )

        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                )

            print(f"Token: {token}")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )

        decoded_token = decode_jwt(token)
        user_id = int(decoded_token.get("sub"))

        if user_id:
            user = await user_service.get_user(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
            )


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_product_repository(
        self,
        session: AsyncSession,
    ) -> ProductRepositoryI:
        return ProductRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_category_repository(
        self,
        session: AsyncSession,
    ) -> CategoryRepositoryI:
        return CategoryRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_image_repository(
        self,
        session: AsyncSession,
    ) -> ProductImageRepositoryI:
        return ProductImageRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_s3_repository(self) -> S3RepositoryI:
        return S3Repository()

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> UserRepositoryI:
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
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

    @provide(scope=Scope.REQUEST)
    def get_categories_service(
        self,
        uow: UnitOfWork,
        category_repository: CategoryRepositoryI,
    ) -> CategoriesService:
        return CategoriesService(uow, category_repository)

    @provide(scope=Scope.REQUEST)
    def get_user_service(
        self,
        uow: UnitOfWork,
        user_repository: UserRepositoryI,
    ) -> UserService:
        return UserService(uow, user_repository)


class ClientProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_s3_client(self) -> S3Client:
        return S3Client()


container = make_async_container(
    DatabaseProvider(),
    RepositoryProvider(),
    ServiceProvider(),
    FastapiProvider(),
    ClientProvider(),
    ConfigProvider(),
    AuthProvider(),
)


def init_dependencies(app) -> None:
    setup_dishka(container, app)
