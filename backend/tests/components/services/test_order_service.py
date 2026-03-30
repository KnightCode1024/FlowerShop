"""Unit tests for OrderService business logic."""

import pytest
from decimal import Decimal

from schemas.order import CartItem, OrderCreate, OrderStatus
from schemas.product import ProductCreate


class TestOrderServiceBusinessLogic:
    """Tests for OrderService business logic (quantity management)."""

    async def test_deduct_product_quantities_after_payment(
        self,
        session,
        created_user,
        order_service,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """OrderService should deduct quantities after payment."""
        # Arrange
        product_data = ProductCreate(
            name="Test Product",
            description="Test",
            price=Decimal("50.00"),
            in_stock=True,
            quantity=10,
            category_id=test_category_for_products.id,
        )
        created_product = await product_repository.create(product_data)

        # Create order in cart
        order_create = OrderCreate(
            user_id=created_user.id,
            order_products=[
                CartItem(product_id=created_product.id, quantity=3, price=50.00)
            ],
        )
        order = await order_repository.add(order_create)

        # Verify quantity not changed yet (still in cart)
        product_before = await product_repository.get_by_id(created_product.id)
        assert product_before.quantity == 10

        # Act - deduct quantities (simulate payment)
        await order_service.deduct_product_quantities(order.id)

        # Assert
        updated_product = await product_repository.get_by_id(created_product.id)
        assert updated_product.quantity == 7  # 10 - 3
        assert updated_product.in_stock is True

    async def test_restore_product_quantities_on_cancel(
        self,
        session,
        created_user,
        order_service,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """OrderService should restore quantities on order cancel."""
        # Arrange
        product_data = ProductCreate(
            name="Cancelable Product",
            description="Test",
            price=Decimal("50.00"),
            in_stock=True,
            quantity=10,
            category_id=test_category_for_products.id,
        )
        created_product = await product_repository.create(product_data)

        # Create and pay for order
        order_create = OrderCreate(
            user_id=created_user.id,
            order_products=[
                CartItem(product_id=created_product.id, quantity=3, price=50.00)
            ],
        )
        order = await order_repository.add(order_create)
        await order_service.deduct_product_quantities(order.id)

        # Verify quantity decreased
        product_after_payment = await product_repository.get_by_id(created_product.id)
        assert product_after_payment.quantity == 7

        # Act - restore quantities (simulate cancellation)
        await order_service.restore_product_quantities(order.id)

        # Assert
        restored_product = await product_repository.get_by_id(created_product.id)
        assert restored_product.quantity == 10  # Back to original
        assert restored_product.in_stock is True

    async def test_deduct_exhausts_product_stock(
        self,
        session,
        created_user,
        order_service,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """OrderService should mark product out of stock when quantity reaches 0."""
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
                CartItem(product_id=created_product.id, quantity=1, price=75.00)
            ],
        )
        order = await order_repository.add(order_create)

        # Act - deduct quantities
        await order_service.deduct_product_quantities(order.id)

        # Assert
        updated_product = await product_repository.get_by_id(created_product.id)
        assert updated_product.quantity == 0
        assert updated_product.in_stock is False

    async def test_deduct_multiple_products(
        self,
        session,
        created_user,
        order_service,
        product_repository,
        order_repository,
        test_category_for_products,
    ):
        """OrderService should deduct quantities for multiple products."""
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
        order = await order_repository.add(order_create)

        # Act
        await order_service.deduct_product_quantities(order.id)

        # Assert
        updated_p1 = await product_repository.get_by_id(product1.id)
        updated_p2 = await product_repository.get_by_id(product2.id)

        assert updated_p1.quantity == 15  # 20 - 5
        assert updated_p2.quantity == 12  # 15 - 3