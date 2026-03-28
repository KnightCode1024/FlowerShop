"""Tests for product inventory/quantity functionality."""

from decimal import Decimal

import pytest
from fastapi import HTTPException

from models import Product
from schemas.order import CartItem, OrderCreate, OrderStatus
from schemas.product import ProductCreate, ProductFilterParams


class TestProductInventory:
    """Tests for product quantity and stock management."""

    async def test_product_with_zero_quantity_not_in_catalog(
        self,
        product_repository,
        test_category_for_products,
    ):
        """Products with quantity=0 should not appear in catalog."""
        # Arrange - create products with different quantities
        product_in_stock = ProductCreate(
            name="In Stock Product",
            description="Available product",
            price=Decimal("29.99"),
            in_stock=True,
            quantity=10,
            category_id=test_category_for_products.id,
        )
        product_out_of_stock = ProductCreate(
            name="Out of Stock Product",
            description="Not available product",
            price=Decimal("19.99"),
            in_stock=False,
            quantity=0,
            category_id=test_category_for_products.id,
        )

        await product_repository.create(product_in_stock)
        await product_repository.create(product_out_of_stock)

        # Act - get products without filters (catalog view)
        filters = ProductFilterParams()
        result = await product_repository.get_filtered(filters)

        # Assert - only product with quantity > 0 should be returned
        assert len(result) == 1
        assert result[0].name == "In Stock Product"
        assert result[0].quantity > 0

    async def test_product_quantity_decreased_on_order(
        self,
        session,
        created_user,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """Product quantity should decrease when order is placed."""
        # Arrange
        product_data = ProductCreate(
            name="Test Product",
            description="Test description",
            price=Decimal("50.00"),
            in_stock=True,
            quantity=10,
            category_id=test_category_for_products.id,
        )
        created_product = await product_repository.create(product_data)

        order_create = OrderCreate(
            user_id=created_user.id,
            order_products=[
                CartItem(
                    product_id=created_product.id,
                    quantity=3,
                    price=50.00,
                )
            ],
        )

        # Act - create order
        order = await order_repository.add(order_create)

        # Assert
        assert order.status == OrderStatus.IN_CART
        assert len(order.order_products) == 1

        # Check product quantity was decreased
        updated_product = await product_repository.get_by_id(created_product.id)
        assert updated_product.quantity == 7  # 10 - 3 = 7
        assert updated_product.in_stock is True

    async def test_cannot_order_more_than_available(
        self,
        session,
        created_user,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """Should raise error when trying to order more than available."""
        # Arrange
        product_data = ProductCreate(
            name="Limited Product",
            description="Limited stock",
            price=Decimal("100.00"),
            in_stock=True,
            quantity=5,
            category_id=test_category_for_products.id,
        )
        created_product = await product_repository.create(product_data)

        order_create = OrderCreate(
            user_id=created_user.id,
            order_products=[
                CartItem(
                    product_id=created_product.id,
                    quantity=10,  # More than available
                    price=100.00,
                )
            ],
        )

        # Act & Assert - should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await order_repository.add(order_create)

        assert exc_info.value.status_code == 400
        assert "insufficient stock" in str(exc_info.value.detail).lower()

    async def test_product_marked_out_of_stock_when_quantity_zero(
        self,
        session,
        created_user,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """Product should be marked as out of stock when quantity reaches 0."""
        # Arrange
        product_data = ProductCreate(
            name="Last Item",
            description="Only one left",
            price=Decimal("75.00"),
            in_stock=True,
            quantity=1,
            category_id=test_category_for_products.id,
        )
        created_product = await product_repository.create(product_data)

        order_create = OrderCreate(
            user_id=created_user.id,
            order_products=[
                CartItem(
                    product_id=created_product.id,
                    quantity=1,
                    price=75.00,
                )
            ],
        )

        # Act - order the last item
        await order_repository.add(order_create)

        # Assert
        updated_product = await product_repository.get_by_id(created_product.id)
        assert updated_product.quantity == 0
        assert updated_product.in_stock is False

    async def test_multiple_products_quantity_update(
        self,
        session,
        created_user,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """Order with multiple products should decrease all quantities."""
        # Arrange
        product1 = await product_repository.create(ProductCreate(
            name="Product 1",
            price=Decimal("10.00"),
            in_stock=True,
            quantity=20,
            category_id=test_category_for_products.id,
        ))
        product2 = await product_repository.create(ProductCreate(
            name="Product 2",
            price=Decimal("20.00"),
            in_stock=True,
            quantity=15,
            category_id=test_category_for_products.id,
        ))

        order_create = OrderCreate(
            user_id=created_user.id,
            order_products=[
                CartItem(product_id=product1.id, quantity=5, price=10.00),
                CartItem(product_id=product2.id, quantity=3, price=20.00),
            ],
        )

        # Act
        await order_repository.add(order_create)

        # Assert
        updated_p1 = await product_repository.get_by_id(product1.id)
        updated_p2 = await product_repository.get_by_id(product2.id)

        assert updated_p1.quantity == 15  # 20 - 5
        assert updated_p2.quantity == 12  # 15 - 3
        assert updated_p1.in_stock is True
        assert updated_p2.in_stock is True

    async def test_partial_order_exhausts_one_product(
        self,
        session,
        created_user,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """Order that exhausts one product should mark it out of stock."""
        # Arrange
        product1 = await product_repository.create(ProductCreate(
            name="Exhaustible Product",
            price=Decimal("30.00"),
            in_stock=True,
            quantity=2,
            category_id=test_category_for_products.id,
        ))
        product2 = await product_repository.create(ProductCreate(
            name="Plenty Product",
            price=Decimal("40.00"),
            in_stock=True,
            quantity=100,
            category_id=test_category_for_products.id,
        ))

        order_create = OrderCreate(
            user_id=created_user.id,
            order_products=[
                CartItem(product_id=product1.id, quantity=2, price=30.00),  # Exhaust
                CartItem(product_id=product2.id, quantity=1, price=40.00),
            ],
        )

        # Act
        await order_repository.add(order_create)

        # Assert
        updated_p1 = await product_repository.get_by_id(product1.id)
        updated_p2 = await product_repository.get_by_id(product2.id)

        assert updated_p1.quantity == 0
        assert updated_p1.in_stock is False
        assert updated_p2.quantity == 99
        assert updated_p2.in_stock is True
