import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.flowershop_api.repositories.order import OrderRepositories
from src.flowershop_api.repositories.user import UserRepository
from src.flowershop_api.repositories.category import CategoryRepository
from src.flowershop_api.repositories.product import ProductRepository
from src.flowershop_api.schemas.user import UserCreate, UserUpdate
from src.flowershop_api.schemas.category import CategoryCreate, CategoryUpdate
from src.flowershop_api.schemas.product import ProductCreate, ProductUpdate, ProductResponse


@pytest.fixture
async def session(async_session_maker):
    async with async_session_maker() as session:
        yield session

        await session.rollback()


@pytest.fixture
def user_repository(session: AsyncSession):
    return UserRepository(session=session)


@pytest.fixture
def category_repository(session: AsyncSession):
    return CategoryRepository(session=session)


@pytest.fixture
def product_repository(session: AsyncSession):
    return ProductRepository(session=session)


@pytest.fixture
def order_repository(session: AsyncSession):
    return OrderRepositories(session=session)


@pytest.fixture
def test_user1():
    return UserCreate(
        email="test_user1@gmail.com",
        username="test_user1",
        password="Qwerty123!",
    )


@pytest.fixture
def test_user2():
    return UserCreate(
        email="test_user2@gmail.com",
        username="test_user2",
        password="Pomidoro567!",
    )


@pytest.fixture
def test_user3():
    return UserCreate(
        email="test_user3@gmail.com",
        username="test_user3",
        password="super-password456!",
    )


@pytest.fixture
def user_update_data():
    return UserUpdate(username="updated_user", email="updated@example.com")


@pytest.fixture
async def created_user(user_repository, test_user1):
    return await user_repository.create(test_user1)


@pytest.fixture
async def multiple_users(user_repository, test_user1, test_user2, test_user3):
    await user_repository.create(test_user1)
    await user_repository.create(test_user2)
    await user_repository.create(test_user3)


@pytest.fixture
def test_category1():
    return CategoryCreate(name="Electronics")


@pytest.fixture
def test_category2():
    return CategoryCreate(name="Books")


@pytest.fixture
def test_category3():
    return CategoryCreate(name="Clothing")


@pytest.fixture
def category_update_data():
    return CategoryUpdate(name="Updated Category")


@pytest.fixture
async def created_category(category_repository, test_category1):
    return await category_repository.create(test_category1)


@pytest.fixture
async def multiple_categories(
        category_repository, test_category1, test_category2, test_category3
):
    await category_repository.create(test_category1)
    await category_repository.create(test_category2)
    await category_repository.create(test_category3)


@pytest.fixture
async def test_category_for_products(category_repository):
    category_data = CategoryCreate(name="Flowers")
    return await category_repository.create(category_data)


@pytest.fixture
def test_product1(test_category_for_products):
    return ProductCreate(
        name="Rose Bouquet",
        description="Beautiful red roses",
        price=Decimal("29.99"),
        in_stock=True,
        category_id=test_category_for_products.id,
    )


@pytest.fixture
def test_product2(test_category_for_products):
    return ProductCreate(
        name="Tulip Arrangement",
        description="Colorful tulips",
        price=Decimal("19.99"),
        in_stock=True,
        category_id=test_category_for_products.id,
    )


@pytest.fixture
def test_product3(test_category_for_products):
    return ProductCreate(
        name="Lily Bouquet",
        description="Elegant white lilies",
        price=Decimal("39.99"),
        in_stock=False,
        category_id=test_category_for_products.id,
    )


@pytest.fixture
def product_update_data():
    return ProductUpdate(
        name="Updated Product Name",
        description="Updated description",
        price=Decimal("49.99"),
        in_stock=False,
    )


@pytest.fixture
async def created_product(product_repository, test_product1):
    return await product_repository.create(test_product1)


@pytest.fixture
async def created_product_2(product_repository, test_product2):
    return await product_repository.create(test_product2)


@pytest.fixture
async def created_multiply_products(product_repository, test_product1, test_product2, test_product3) -> list[ProductResponse]:
    return [
        await product_repository.create(test_product1),
        await product_repository.create(test_product2),
        await product_repository.create(test_product3)
    ]


@pytest.fixture
async def multiple_products(
        product_repository, test_product1, test_product2, test_product3
):
    await product_repository.create(test_product1)
    await product_repository.create(test_product2)
    await product_repository.create(test_product3)
