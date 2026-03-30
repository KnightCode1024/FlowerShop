"""Integration tests for order delivery address functionality."""

import random
import pytest
from decimal import Decimal

from schemas.category import CategoryCreate, CategoryResponse
from schemas.product import CreateProductRequest, ProductResponse
from schemas.order import OrderCreateRequest, DeliveryAddress, OrderResponse


class TestOrderAddressIntegration:
    """Integration tests for delivery address in orders via API."""

    @pytest.mark.asyncio
    async def test_create_order_with_delivery_address(self, created_admin_client, created_user_session):
        """Test creating an order with delivery address via API."""
        client, user = created_user_session

        # Arrange - create category and product
        category_data = CategoryCreate(name=f"address_test_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"Address test product {random.randint(1, 1000)}",
            price=Decimal("100.00"),
            in_stock=True,
            quantity=10,
            category_id=category.id,
        )
        create_response = await client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )
        product = ProductResponse(**create_response.json())

        # Act - create order with delivery address
        delivery_address = DeliveryAddress(
            recipient_name="Иван Иванов",
            recipient_phone="+79991234567",
            delivery_address="ул. Примерная, д. 10, кв. 50",
            delivery_city="Москва",
            delivery_zip="123456",
            delivery_notes="Домофон 123",
        )

        order_request = OrderCreateRequest(
            order_products=[
                {"product_id": product.id, "quantity": 2, "price": 100.00}
            ],
            delivery_address=delivery_address,
        )

        response = await client.post(
            "/orders/",
            json=order_request.model_dump(),
        )

        # Assert
        assert response.status_code == 200, f"Failed: {response.text}"
        order = OrderResponse(**response.json())
        
        # Note: OrderResponse from API may not include address in cart status
        # Address is typically set during checkout

    @pytest.mark.asyncio
    async def test_update_cart_with_delivery_address(self, created_admin_client, created_user_session):
        """Test updating cart with delivery address."""
        client, user = created_user_session

        # Arrange - create category and product
        category_data = CategoryCreate(name=f"cart_addr_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"Cart address product {random.randint(1, 1000)}",
            price=Decimal("50.00"),
            in_stock=True,
            quantity=20,
            category_id=category.id,
        )
        create_response = await client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )
        product = ProductResponse(**create_response.json())

        # Act - update cart with delivery address
        delivery_address = DeliveryAddress(
            recipient_name="Петр Петров",
            recipient_phone="+79997654321",
            delivery_address="пр. Ленина, д. 5",
            delivery_city="Санкт-Петербург",
            delivery_zip="190000",
        )

        order_request = OrderCreateRequest(
            order_products=[
                {"product_id": product.id, "quantity": 3, "price": 50.00}
            ],
            delivery_address=delivery_address,
        )

        response = await client.put(
            "/orders/cart",
            json=order_request.model_dump(),
        )

        # Assert
        assert response.status_code == 200, f"Failed: {response.text}"
        order = response.json()
        
        # Verify address was saved
        assert order.get("recipient_name") == "Петр Петров"
        assert order.get("recipient_phone") == "+79997654321"
        assert order.get("delivery_address") == "пр. Ленина, д. 5"
        assert order.get("delivery_city") == "Санкт-Петербург"
        assert order.get("delivery_zip") == "190000"

    @pytest.mark.asyncio
    async def test_get_cart_includes_delivery_address(self, created_admin_client, created_user_session):
        """Test that getting cart returns delivery address."""
        client, user = created_user_session

        # Arrange - create category and product
        category_data = CategoryCreate(name=f"get_cart_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"Get cart product {random.randint(1, 1000)}",
            price=Decimal("75.00"),
            in_stock=True,
            quantity=15,
            category_id=category.id,
        )
        create_response = await client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )
        product = ProductResponse(**create_response.json())

        # Set cart with address
        delivery_address = DeliveryAddress(
            recipient_name="Анна Сидорова",
            recipient_phone="+79991112233",
            delivery_address="бульвар Цветной, д. 15",
            delivery_city="Казань",
            delivery_zip="420000",
            delivery_notes="Позвонить за 30 минут",
        )

        await client.put(
            "/orders/cart",
            json={
                "order_products": [{"product_id": product.id, "quantity": 1, "price": 75.00}],
                "delivery_address": delivery_address.model_dump(),
            },
        )

        # Act - get cart
        response = await client.get("/orders/cart")

        # Assert
        assert response.status_code == 200
        order = response.json()
        assert order["recipient_name"] == "Анна Сидорова"
        assert order["recipient_phone"] == "+79991112233"
        assert order["delivery_address"] == "бульвар Цветной, д. 15"
        assert order["delivery_city"] == "Казань"
        assert order["delivery_notes"] == "Позвонить за 30 минут"

    @pytest.mark.asyncio
    async def test_update_delivery_address_only(self, created_admin_client, created_user_session):
        """Test updating only delivery address without changing products."""
        client, user = created_user_session

        # Arrange - create category and product
        category_data = CategoryCreate(name=f"update_addr_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"Update address product {random.randint(1, 1000)}",
            price=Decimal("200.00"),
            in_stock=True,
            quantity=5,
            category_id=category.id,
        )
        create_response = await client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )
        product = ProductResponse(**create_response.json())

        # First set cart with initial address
        initial_address = DeliveryAddress(
            recipient_name="Иван Иванов",
            recipient_phone="+79991234567",
            delivery_address="ул. Первая, д. 1",
            delivery_city="Москва",
        )

        await client.put(
            "/orders/cart",
            json={
                "order_products": [{"product_id": product.id, "quantity": 1, "price": 200.00}],
                "delivery_address": initial_address.model_dump(),
            },
        )

        # Act - update address only
        new_address = DeliveryAddress(
            recipient_name="Петр Петров",
            recipient_phone="+79999999999",
            delivery_address="ул. Вторая, д. 2",
            delivery_city="Санкт-Петербург",
            delivery_zip="190000",
        )

        response = await client.put(
            "/orders/cart",
            json={
                "order_products": [{"product_id": product.id, "quantity": 1, "price": 200.00}],
                "delivery_address": new_address.model_dump(),
            },
        )

        # Assert
        assert response.status_code == 200
        order = response.json()
        assert order["recipient_name"] == "Петр Петров"
        assert order["delivery_city"] == "Санкт-Петербург"

    @pytest.mark.asyncio
    async def test_order_without_delivery_address(self, created_admin_client, created_user_session):
        """Test that orders can be created without delivery address (backward compatibility)."""
        client, user = created_user_session

        # Arrange - create category and product
        category_data = CategoryCreate(name=f"no_addr_cat_{random.randint(1, 1000)}")
        category_response = await client.post("/categories/", json=category_data.model_dump())
        category = CategoryResponse(**category_response.json())

        product_data = CreateProductRequest(
            name=f"No address product {random.randint(1, 1000)}",
            price=Decimal("150.00"),
            in_stock=True,
            quantity=10,
            category_id=category.id,
        )
        create_response = await client.post(
            "/products/",
            data={"product_data": product_data.model_dump_json()},
        )
        product = ProductResponse(**create_response.json())

        # Act - create order without delivery address
        response = await client.put(
            "/orders/cart",
            json={
                "order_products": [{"product_id": product.id, "quantity": 2, "price": 150.00}],
            },
        )

        # Assert
        assert response.status_code == 200
        order = response.json()
        # Address fields should be None or not present
        assert order.get("recipient_name") is None
        assert order.get("delivery_address") is None
