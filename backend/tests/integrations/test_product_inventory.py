"""Integration tests for product inventory/quantity functionality."""

import random
import pytest
from decimal import Decimal

from schemas.category import CategoryCreate, CategoryResponse
from schemas.product import CreateProductRequest, ProductResponse, UpdateProductRequest
from schemas.order import OrderCreate, CartItem, OrderStatus


class TestProductInventoryIntegration:
    """Integration tests for product quantity management via API."""

    @pytest.mark.asyncio
    async def test_create_product_with_quantity(self, created_admin_client):
        """Test creating a product with quantity via API."""
        # Arrange - create category
        category_data = CategoryCreate(name=f"inventory_test_cat_{random.randint(1, 1000)}")
        category_response = await created_admin_client.post(
            "/categories/",
            json=category_data.model_dump(),
        )
        category = CategoryResponse(**category_response.json())

        # Act - create product with quantity
        product_data = CreateProductRequest(
            name=f"Product with stock {random.randint(1, 1000)}",
            description="Test product with inventory",
            price=Decimal("99.99"),
            in_stock=True,
            quantity=50,
            category_id=category.id,
        )

        response = await created_admin_client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )

        # Assert
        assert response.status_code == 200, f"Failed: {response.text}"
        product = ProductResponse(**response.json())
        assert product.quantity == 50
        assert product.in_stock is True

    @pytest.mark.asyncio
    async def test_update_product_quantity(self, created_admin_client, created_product):
        """Test updating product quantity via API."""
        # Arrange
        product_id = created_product.id

        # Act - update quantity
        update_data = UpdateProductRequest(
            quantity=25,
        )

        response = await created_admin_client.put(
            f"/products/{product_id}",
            data={"product_data": update_data.model_dump_json()},
        )

        # Assert
        assert response.status_code == 200, f"Failed: {response.text}"
        updated_product = ProductResponse(**response.json())
        assert updated_product.quantity == 25

    @pytest.mark.asyncio
    async def test_zero_quantity_product_not_in_catalog(self, created_admin_client):
        """Test that products with quantity=0 are not visible in public catalog."""
        # Arrange - create category and product with zero quantity
        category_data = CategoryCreate(name=f"zero_stock_cat_{random.randint(1, 1000)}")
        category_response = await created_admin_client.post(
            "/categories/",
            json=category_data.model_dump(),
        )
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"Out of stock product {random.randint(1, 1000)}",
            description="Should not appear in catalog",
            price=Decimal("49.99"),
            in_stock=True,
            quantity=0,  # Zero quantity
            category_id=category.id,
        )

        await created_admin_client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )

        # Also create a product with stock
        product_in_stock = CreateProductRequest(
            name=f"In stock product {random.randint(1, 1000)}",
            description="Should appear in catalog",
            price=Decimal("59.99"),
            in_stock=True,
            quantity=10,
            category_id=category.id,
        )

        await created_admin_client.post(
            "/products/",
            data={"product_data": product_in_stock.model_dump_json()},
        )

        # Act - get public catalog
        response = await created_admin_client.get("/products/")
        products = response.json()

        # Assert - only product with quantity > 0 should be in catalog
        assert response.status_code == 200
        assert len(products) == 1
        assert products[0]["name"] == product_in_stock.name
        assert products[0]["quantity"] > 0

    @pytest.mark.asyncio
    async def test_order_decreases_product_quantity(self, created_admin_client, created_user_session):
        """Test that placing an order decreases product quantity."""
        client, user = created_user_session

        # Arrange - create category and product
        category_data = CategoryCreate(name=f"order_test_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"Order test product {random.randint(1, 1000)}",
            description="Test product for order",
            price=Decimal("100.00"),
            in_stock=True,
            quantity=20,
            category_id=category.id,
        )

        create_response = await client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )
        product = ProductResponse(**create_response.json())

        # Act - place order
        order_data = OrderCreate(
            user_id=user.id,
            order_products=[
                CartItem(
                    product_id=product.id,
                    quantity=5,
                    price=100.00,
                )
            ],
        )

        order_response = await client.post(
            "/orders/",
            json=order_data.model_dump(),
        )

        # Assert
        assert order_response.status_code == 200, f"Order failed: {order_response.text}"
        assert order_response.json()["status"] == OrderStatus.IN_CART.value

        # Check product quantity was decreased
        product_response = await client.get(f"/products/{product.id}")
        updated_product = ProductResponse(**product_response.json())
        assert updated_product.quantity == 15  # 20 - 5 = 15
        assert updated_product.in_stock is True

    @pytest.mark.asyncio
    async def test_cannot_order_more_than_available(self, created_admin_client, created_user_session):
        """Test that ordering more than available quantity fails."""
        client, user = created_user_session

        # Arrange - create product with limited stock
        category_data = CategoryCreate(name=f"limited_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"Limited product {random.randint(1, 1000)}",
            description="Limited stock product",
            price=Decimal("200.00"),
            in_stock=True,
            quantity=3,  # Only 3 in stock
            category_id=category.id,
        )

        create_response = await client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )
        product = ProductResponse(**create_response.json())

        # Act & Assert - try to order more than available
        order_data = OrderCreate(
            user_id=user.id,
            order_products=[
                CartItem(
                    product_id=product.id,
                    quantity=10,  # More than 3 available
                    price=200.00,
                )
            ],
        )

        order_response = await client.post(
            "/orders/",
            json=order_data.model_dump(),
        )

        assert order_response.status_code == 400
        assert "insufficient stock" in order_response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_exhausting_stock_marks_product_out_of_stock(
        self, created_admin_client, created_user_session
    ):
        """Test that exhausting all stock marks product as out of stock."""
        client, user = created_user_session

        # Arrange - create product with 1 item
        category_data = CategoryCreate(name=f"exhaust_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"Last item product {random.randint(1, 1000)}",
            description="Only one in stock",
            price=Decimal("500.00"),
            in_stock=True,
            quantity=1,  # Only 1 in stock
            category_id=category.id,
        )

        create_response = await client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )
        product = ProductResponse(**create_response.json())

        # Act - order the last item
        order_data = OrderCreate(
            user_id=user.id,
            order_products=[
                CartItem(
                    product_id=product.id,
                    quantity=1,
                    price=500.00,
                )
            ],
        )

        order_response = await client.post(
            "/orders/",
            json=order_data.model_dump(),
        )

        # Assert
        assert order_response.status_code == 200

        # Product should now be out of stock
        product_response = await client.get(f"/products/{product.id}")
        updated_product = ProductResponse(**product_response.json())
        assert updated_product.quantity == 0
        assert updated_product.in_stock is False

        # Product should not appear in catalog
        catalog_response = await client.get("/products/")
        catalog_products = catalog_response.json()
        product_ids = [p["id"] for p in catalog_products]
        assert product.id not in product_ids

    @pytest.mark.asyncio
    async def test_multiple_products_order_quantity_update(
        self, created_admin_client, created_user_session
    ):
        """Test ordering multiple products decreases all quantities correctly."""
        client, user = created_user_session

        # Arrange - create category and multiple products
        category_data = CategoryCreate(name=f"multi_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        # Create product 1
        product1_data = CreateProductRequest(
            name=f"Multi product 1 {random.randint(1, 1000)}",
            price=Decimal("50.00"),
            in_stock=True,
            quantity=30,
            category_id=category.id,
        )
        p1_response = await client.post(
            "/products/",
            data={"product_data": product1_data.model_dump_json()},
        )
        product1 = ProductResponse(**p1_response.json())

        # Create product 2
        product2_data = CreateProductRequest(
            name=f"Multi product 2 {random.randint(1, 1000)}",
            price=Decimal("75.00"),
            in_stock=True,
            quantity=25,
            category_id=category.id,
        )
        p2_response = await client.post(
            "/products/",
            data={"product_data": product2_data.model_dump_json()},
        )
        product2 = ProductResponse(**p2_response.json())

        # Act - order both products
        order_data = OrderCreate(
            user_id=user.id,
            order_products=[
                CartItem(product_id=product1.id, quantity=10, price=50.00),
                CartItem(product_id=product2.id, quantity=5, price=75.00),
            ],
        )

        order_response = await client.post(
            "/orders/",
            json=order_data.model_dump(),
        )

        # Assert
        assert order_response.status_code == 200

        # Check both quantities decreased
        p1_updated = ProductResponse(**(await client.get(f"/products/{product1.id}")).json())
        p2_updated = ProductResponse(**(await client.get(f"/products/{product2.id}")).json())

        assert p1_updated.quantity == 20  # 30 - 10
        assert p2_updated.quantity == 20  # 25 - 5
        assert p1_updated.in_stock is True
        assert p2_updated.in_stock is True

    @pytest.mark.asyncio
    async def test_admin_can_see_all_products_including_out_of_stock(
        self, created_admin_client
    ):
        """Test that admin API returns all products including those with quantity=0."""
        # Arrange - create category
        category_data = CategoryCreate(name=f"admin_view_cat_{random.randint(1, 1000)}")
        category_response = await created_admin_client.post(
            "/categories/",
            json=category_data.model_dump(),
        )
        category = CategoryResponse(**category_response.json())

        # Create product with stock
        in_stock_product = CreateProductRequest(
            name=f"Admin visible product {random.randint(1, 1000)}",
            price=Decimal("100.00"),
            in_stock=True,
            quantity=10,
            category_id=category.id,
        )
        await created_admin_client.post(
            "/products/",
            data={"product_data": in_stock_product.model_dump_json()},
        )

        # Create product without stock
        out_of_stock_product = CreateProductRequest(
            name=f"Admin zero stock product {random.randint(1, 1000)}",
            price=Decimal("150.00"),
            in_stock=False,
            quantity=0,
            category_id=category.id,
        )
        await created_admin_client.post(
            "/products/",
            data={"product_data": out_of_stock_product.model_dump_json()},
        )

        # Act - admin gets all products
        response = await created_admin_client.get("/products/?limit=100")
        products = response.json()

        # Assert - admin should see both products
        assert response.status_code == 200
        assert len(products) == 2
        product_names = [p["name"] for p in products]
        assert in_stock_product.name in product_names
        assert out_of_stock_product.name in product_names
