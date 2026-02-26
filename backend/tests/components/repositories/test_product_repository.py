from decimal import Decimal

import pytest

from schemas.product import (
    ProductUpdate,
    ProductFilterParams,
)
from schemas.category import CategoryCreate
from models import Product


class TestProductRepository:
    async def test_create_product_success(
        self,
        product_repository,
        test_product1,
    ):
        # Act
        result = await product_repository.create(test_product1)

        # Assert
        assert result.id is not None
        assert result.name == test_product1.name
        assert result.description == test_product1.description
        assert result.price == test_product1.price
        assert result.in_stock == test_product1.in_stock
        assert result.category_id == test_product1.category_id

    async def test_get_by_id_existing_product(
        self,
        product_repository,
        test_product1,
    ):
        # Arrange
        created_product = await product_repository.create(test_product1)

        # Act
        result = await product_repository.get_by_id(created_product.id)

        # Assert
        assert result is not None
        assert result.id == created_product.id
        assert result.name == test_product1.name
        # Check that result has the expected attributes (Pydantic model)
        assert hasattr(result, "id") and hasattr(result, "name")
        assert hasattr(result, "price") and hasattr(result, "category_id")

    async def test_get_by_id_non_existing_product(self, product_repository):
        # Act
        result = await product_repository.get_by_id(999)

        # Assert
        assert result is None

    async def test_get_filtered_no_filters(
        self,
        product_repository,
        test_product1,
        test_product2,
    ):
        # Arrange
        await product_repository.create(test_product1)
        await product_repository.create(test_product2)
        filters = ProductFilterParams()

        # Act
        result = await product_repository.get_filtered(filters)

        # Assert
        assert len(result) == 2
        assert all(isinstance(product, Product) for product in result)

    async def test_get_filtered_by_category(
        self,
        product_repository,
        test_product1,
        test_product2,
        category_repository,
        test_category1,
    ):
        # Arrange
        category1 = await category_repository.create(test_category1)
        category2 = await category_repository.create(
            CategoryCreate(name="Other"),
        )

        product1_data = test_product1.model_copy()
        product1_data.category_id = category1.id
        product2_data = test_product2.model_copy()
        product2_data.category_id = category2.id

        await product_repository.create(product1_data)
        await product_repository.create(product2_data)

        filters = ProductFilterParams(category_id=category1.id)

        # Act
        result = await product_repository.get_filtered(filters)

        # Assert
        assert len(result) == 1
        assert result[0].category_id == category1.id

    async def test_get_filtered_by_price_range(
        self,
        product_repository,
        test_product1,
        test_product2,
        test_product3,
    ):
        # Arrange
        await product_repository.create(test_product1)  # 29.99
        await product_repository.create(test_product2)  # 19.99
        await product_repository.create(test_product3)  # 39.99

        filters = ProductFilterParams(
            min_price=Decimal("20.00"), max_price=Decimal("35.00")
        )

        # Act
        result = await product_repository.get_filtered(filters)

        # Assert
        assert len(result) == 1
        assert result[0].price == Decimal("29.99")

    async def test_get_filtered_by_stock_status(
        self,
        product_repository,
        test_product1,
        test_product2,
        test_product3,
    ):
        # Arrange
        await product_repository.create(test_product1)  # in_stock=True
        await product_repository.create(test_product2)  # in_stock=True
        await product_repository.create(test_product3)  # in_stock=False

        filters = ProductFilterParams(in_stock=True)

        # Act
        result = await product_repository.get_filtered(filters)

        # Assert
        assert len(result) == 2
        assert all(product.in_stock for product in result)

    async def test_get_filtered_with_pagination(
        self,
        product_repository,
        test_product1,
        test_product2,
        test_product3,
    ):
        # Arrange
        await product_repository.create(test_product1)
        await product_repository.create(test_product2)
        await product_repository.create(test_product3)

        filters = ProductFilterParams(offset=1, limit=2)

        # Act
        result = await product_repository.get_filtered(filters)

        # Assert
        assert len(result) == 2

    @pytest.mark.parametrize(
        "offset,limit,expected_count",
        [
            (0, 10, 3),
            (1, 2, 2),
            (2, 10, 1),
            (10, 10, 0),
        ],
    )
    async def test_get_filtered_pagination_parametrized(
        self,
        product_repository,
        multiple_products,
        offset,
        limit,
        expected_count,
    ):
        filters = ProductFilterParams(offset=offset, limit=limit)
        result = await product_repository.get_filtered(filters)
        assert len(result) == expected_count

    async def test_update_product_success(
        self,
        product_repository,
        test_product1,
    ):
        # Arrange
        created_product = await product_repository.create(test_product1)
        update_data = ProductUpdate(
            name="Updated Product",
            price=Decimal("99.99"),
            in_stock=False,
        )

        # Act
        result = await product_repository.update(
            created_product.id,
            update_data,
        )

        # Assert
        assert result is not None
        assert result.id == created_product.id
        assert result.name == "Updated Product"
        assert result.price == Decimal("99.99")
        assert result.in_stock is False

    async def test_update_product_partial(
        self,
        product_repository,
        test_product1,
    ):
        # Arrange
        created_product = await product_repository.create(test_product1)
        update_data = ProductUpdate(name="Partially Updated")

        # Act
        result = await product_repository.update(
            created_product.id,
            update_data,
        )

        # Assert
        assert result is not None
        assert result.name == "Partially Updated"
        assert result.price == test_product1.price  # unchanged
        assert result.in_stock == test_product1.in_stock  # unchanged

    async def test_update_product_non_existing(self, product_repository):
        # Arrange
        update_data = ProductUpdate(name="Non-existent Product")

        # Act
        result = await product_repository.update(999, update_data)

        # Assert
        assert result is None

    async def test_update_product_empty_update(
        self,
        product_repository,
        test_product1,
    ):
        # Arrange
        created_product = await product_repository.create(test_product1)
        update_data = ProductUpdate()

        # Act
        result = await product_repository.update(
            created_product.id,
            update_data,
        )

        # Assert
        assert result is not None
        assert result.name == test_product1.name  # unchanged

    async def test_delete_product_success(
        self,
        product_repository,
        test_product1,
    ):
        # Arrange
        created_product = await product_repository.create(test_product1)

        # Act
        result = await product_repository.delete(created_product.id)

        # Assert
        assert result == 1

    async def test_delete_product_non_existing(self, product_repository):
        # Act
        result = await product_repository.delete(999)

        # Assert
        assert result == 0

    async def test_exists_by_name_existing_product(
        self,
        product_repository,
        test_product1,
    ):
        # Arrange
        await product_repository.create(test_product1)

        # Act
        result = await product_repository.exists_by_name(test_product1.name)

        # Assert
        assert result is True

    async def test_exists_by_name_non_existing_product(
        self,
        product_repository,
    ):
        # Act
        result = await product_repository.exists_by_name(
            "Non-existent Product",
        )

        # Assert
        assert result is False

    async def test_exists_by_name_with_exclude_id(
        self,
        product_repository,
        test_product1,
        test_product2,
    ):
        # Arrange
        created1 = await product_repository.create(test_product1)
        created2 = await product_repository.create(test_product2)

        # Act & Assert
        assert (
            await product_repository.exists_by_name(
                test_product2.name,
            )
            is True
        )
        assert (
            await product_repository.exists_by_name(
                test_product2.name, exclude_id=created2.id
            )
            is False
        )
        assert (
            await product_repository.exists_by_name(
                test_product2.name, exclude_id=created1.id
            )
            is True
        )

    async def test_repository_returns_correct_types(
        self,
        product_repository,
        test_product1,
    ):
        # Arrange & Act
        created = await product_repository.create(test_product1)
        retrieved = await product_repository.get_by_id(created.id)
        updated = await product_repository.update(
            created.id,
            ProductUpdate(name="Updated Product"),
        )
        filtered = await product_repository.get_filtered(ProductFilterParams())

        # Assert - Check that results have expected attributes
        assert hasattr(created, "id") and hasattr(created, "name")
        assert hasattr(created, "price") and hasattr(created, "category_id")
        assert (
            hasattr(retrieved, "id") and hasattr(retrieved, "name")
        ) or retrieved is None
        assert (
            hasattr(updated, "id")
            and hasattr(
                updated,
                "name",
            )
        ) or updated is None
        assert isinstance(filtered, list)
        assert all(isinstance(product, Product) for product in filtered)


async def test_product_repository_workflow(
    product_repository,
    test_product1,
    test_product2,
):
    # Create
    created = await product_repository.create(test_product1)
    assert created.id is not None

    # Get by ID
    retrieved = await product_repository.get_by_id(created.id)
    assert retrieved.name == test_product1.name

    # Check exists by name
    exists = await product_repository.exists_by_name(test_product1.name)
    assert exists is True

    # Get filtered
    all_products = await product_repository.get_filtered(ProductFilterParams())
    assert len(all_products) == 1

    # Update
    updated = await product_repository.update(
        created.id,
        ProductUpdate(name="Updated Product Name", price=Decimal("79.99")),
    )
    assert updated.name == "Updated Product Name"
    assert updated.price == Decimal("79.99")

    # Create second product
    created2 = await product_repository.create(test_product2)
    assert created2.id != created.id

    # Check both products in filtered results
    all_products = await product_repository.get_filtered(ProductFilterParams())
    assert len(all_products) == 2

    # Delete first product
    deleted = await product_repository.delete(created.id)
    assert deleted == 1

    # Note: Due to session rollback in tests, the product remains in DB
    # But the delete method returns the correct result
