
import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from models import RoleEnum

from repositories import OrderRepository, PromocodeRepository
from repositories.invoice import InvoiceRepository
from repositories.user import UserRepository
from repositories.category import CategoryRepository
from repositories.product import ProductRepository
from schemas.user import UserCreate, UserUpdate, UserCreateConsole
from schemas.category import CategoryCreate, CategoryUpdate
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from services.order import OrderService
from core.uow import UnitOfWork


@pytest.fixture
async def session(async_session_maker):
    async with async_session_maker() as session:
        yield session

        await session.rollback()


@pytest.fixture
async def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session=session)


@pytest.fixture
async def category_repository(session: AsyncSession) -> CategoryRepository:
    return CategoryRepository(session=session)


@pytest.fixture
async def product_repository(session: AsyncSession) -> ProductRepository:
    return ProductRepository(session=session)


@pytest.fixture
async def order_repository(session: AsyncSession) -> OrderRepository:
    return OrderRepository(session=session)


@pytest.fixture
async def promocode_repository(session: AsyncSession) -> PromocodeRepository:
    return PromocodeRepository(session=session)


@pytest.fixture
async def invoice_repository(session: AsyncSession) -> InvoiceRepository:
    return InvoiceRepository(session=session)


@pytest.fixture
async def test_category1():
    return CategoryCreate(name="Category 1")


@pytest.fixture
async def test_category2():
    return CategoryCreate(name="Category 2")


@pytest.fixture
async def test_category_for_products(category_repository: CategoryRepository):
    category_data = CategoryCreate(name="Flowers")
    return await category_repository.create(category_data)


@pytest.fixture
def test_product1(test_category_for_products):
    return ProductCreate(
        name="Rose Bouquet",
        description="Beautiful red roses",
        price=Decimal("29.99"),
        in_stock=True,
        quantity=10,
        category_id=test_category_for_products.id,
    )


@pytest.fixture
def test_product2(test_category_for_products):
    return ProductCreate(
        name="Tulip Arrangement",
        description="Colorful tulips",
        price=Decimal("19.99"),
        in_stock=True,
        quantity=5,
        category_id=test_category_for_products.id,
    )


@pytest.fixture
def test_product3(test_category_for_products):
    return ProductCreate(
        name="Lily Bouquet",
        description="Elegant white lilies",
        price=Decimal("39.99"),
        in_stock=False,
        quantity=0,
        category_id=test_category_for_products.id,
    )


@pytest.fixture
def product_update_data():
    return ProductUpdate(
        name="Updated Product Name",
        description="Updated description",
        price=Decimal("99.99"),
        in_stock=False,
    )


@pytest.fixture
async def created_user(user_repository: UserRepository) -> UserCreate:
    user_data = UserCreate(
        email=f"test_{id} @test.com",
        username="testuser",
        password="hashed_password",
        role=RoleEnum.USER,
    )
    return await user_repository.create(user_data)


@pytest.fixture
async def created_product(product_repository: ProductRepository, test_product1):
    return await product_repository.create(test_product1)


@pytest.fixture
async def created_multiply_products(product_repository: ProductRepository, test_product1, test_product2, test_product3) -> list[ProductResponse]:
    return [
        await product_repository.create(test_product1),
        await product_repository.create(test_product2),
        await product_repository.create(test_product3)
    ]


@pytest.fixture
def test_user1():
    return UserCreate(
        email=f"test_user1_{id()}@test.com",
        username="testuser1",
        password="hashed_password",
        role=RoleEnum.USER,
    )


@pytest.fixture
def test_user2():
    return UserCreate(
        email=f"test_user2_{id()}@test.com",
        username="testuser2",
        password="hashed_password",
        role=RoleEnum.USER,
    )


@pytest.fixture
def test_user3():
    return UserCreate(
        email=f"test_user3_{id()}@test.com",
        username="testuser3",
        password="hashed_password",
        role=RoleEnum.USER,
    )


@pytest.fixture
async def order_service(
    session: AsyncSession,
    order_repository: OrderRepository,
    product_repository: ProductRepository,
) -> OrderService:
    """Create OrderService for testing business logic."""
    uow = UnitOfWork(session)
    return OrderService(uow, order_repository, product_repository)
