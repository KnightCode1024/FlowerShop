"""Unit tests for order delivery address functionality."""

import pytest
from decimal import Decimal

from schemas.order import (
    CartItem,
    OrderCreate,
    OrderCreateRequest,
    OrderUpdate,
    OrderResponse,
    OrderStatus,
    DeliveryAddress,
)
from models.order import Order


class TestDeliveryAddressSchema:
    """Tests for DeliveryAddress schema validation."""

    def test_delivery_address_valid(self):
        """Test valid delivery address creation."""
        address = DeliveryAddress(
            recipient_name="Иван Иванов",
            recipient_phone="+7 (999) 123-45-67",
            delivery_address="ул. Примерная, д. 10",
            delivery_city="Москва",
            delivery_zip="123456",
            delivery_notes="Домофон 123",
        )
        assert address.recipient_name == "Иван Иванов"
        assert address.recipient_phone == "+7 (999) 123-45-67"
        assert address.delivery_address == "ул. Примерная, д. 10"
        assert address.delivery_city == "Москва"
        assert address.delivery_zip == "123456"
        assert address.delivery_notes == "Домофон 123"

    def test_delivery_address_minimal(self):
        """Test minimal valid delivery address (required fields only)."""
        address = DeliveryAddress(
            recipient_name="Иван Иванов",
            recipient_phone="+79991234567",
            delivery_address="ул. Примерная, д. 10",
            delivery_city="Москва",
        )
        assert address.recipient_name == "Иван Иванов"
        assert address.delivery_zip is None
        assert address.delivery_notes is None

    def test_delivery_address_empty_name_fails(self):
        """Test that empty recipient_name raises validation error."""
        with pytest.raises(ValueError):
            DeliveryAddress(
                recipient_name="",
                recipient_phone="+79991234567",
                delivery_address="ул. Примерная, д. 10",
                delivery_city="Москва",
            )

    def test_delivery_address_empty_phone_fails(self):
        """Test that empty recipient_phone raises validation error."""
        with pytest.raises(ValueError):
            DeliveryAddress(
                recipient_name="Иван Иванов",
                recipient_phone="",
                delivery_address="ул. Примерная, д. 10",
                delivery_city="Москва",
            )

    def test_delivery_address_empty_address_fails(self):
        """Test that empty delivery_address raises validation error."""
        with pytest.raises(ValueError):
            DeliveryAddress(
                recipient_name="Иван Иванов",
                recipient_phone="+79991234567",
                delivery_address="",
                delivery_city="Москва",
            )

    def test_delivery_address_empty_city_fails(self):
        """Test that empty delivery_city raises validation error."""
        with pytest.raises(ValueError):
            DeliveryAddress(
                recipient_name="Иван Иванов",
                recipient_phone="+79991234567",
                delivery_address="ул. Примерная, д. 10",
                delivery_city="",
            )


class TestOrderCreateRequestWithAddress:
    """Tests for OrderCreateRequest with delivery address."""

    def test_order_create_request_with_address(self):
        """Test creating order request with delivery address."""
        address = DeliveryAddress(
            recipient_name="Иван Иванов",
            recipient_phone="+79991234567",
            delivery_address="ул. Примерная, д. 10",
            delivery_city="Москва",
        )
        request = OrderCreateRequest(
            order_products=[
                CartItem(product_id=1, quantity=2, price=100.00)
            ],
            delivery_address=address,
        )
        assert len(request.order_products) == 1
        assert request.delivery_address is not None
        assert request.delivery_address.recipient_name == "Иван Иванов"

    def test_order_create_request_without_address(self):
        """Test creating order request without delivery address (optional)."""
        request = OrderCreateRequest(
            order_products=[
                CartItem(product_id=1, quantity=2, price=100.00)
            ],
        )
        assert request.delivery_address is None


class TestOrderCreateWithAddress:
    """Tests for OrderCreate model with address fields."""

    def test_order_create_with_full_address(self):
        """Test OrderCreate with all address fields."""
        order = OrderCreate(
            user_id=1,
            order_products=[CartItem(product_id=1, quantity=1, price=50.00)],
            recipient_name="Иван Иванов",
            recipient_phone="+79991234567",
            delivery_address="ул. Примерная, д. 10",
            delivery_city="Москва",
            delivery_zip="123456",
            delivery_notes="Домофон 123",
        )
        assert order.recipient_name == "Иван Иванов"
        assert order.recipient_phone == "+79991234567"
        assert order.delivery_address == "ул. Примерная, д. 10"
        assert order.delivery_city == "Москва"
        assert order.delivery_zip == "123456"
        assert order.delivery_notes == "Домофон 123"

    def test_order_create_without_address(self):
        """Test OrderCreate without address fields (all optional)."""
        order = OrderCreate(
            user_id=1,
            order_products=[CartItem(product_id=1, quantity=1, price=50.00)],
        )
        assert order.recipient_name is None
        assert order.recipient_phone is None
        assert order.delivery_address is None
        assert order.delivery_city is None
        assert order.delivery_zip is None
        assert order.delivery_notes is None


class TestOrderUpdateWithAddress:
    """Tests for OrderUpdate with address fields."""

    def test_order_update_with_address(self):
        """Test updating order with address fields."""
        update = OrderUpdate(
            id=1,
            user_id=1,
            recipient_name="Петр Петров",
            recipient_phone="+79997654321",
            delivery_address="пр. Новый, д. 5",
            delivery_city="Санкт-Петербург",
        )
        assert update.recipient_name == "Петр Петров"
        assert update.delivery_city == "Санкт-Петербург"

    def test_order_update_partial_address(self):
        """Test partially updating order address."""
        update = OrderUpdate(
            id=1,
            user_id=1,
            delivery_notes="Оставить у двери",
        )
        assert update.delivery_notes == "Оставить у двери"
        assert update.recipient_name is None


class TestOrderResponseWithAddress:
    """Tests for OrderResponse with address fields."""

    def test_order_response_with_address(self):
        """Test OrderResponse includes address fields."""
        response = OrderResponse(
            id=1,
            order_products=[CartItem(product_id=1, quantity=1, price=50.00)],
            amount=50.00,
            status=OrderStatus.IN_CART,
            recipient_name="Иван Иванов",
            recipient_phone="+79991234567",
            delivery_address="ул. Примерная, д. 10",
            delivery_city="Москва",
            delivery_zip="123456",
            delivery_notes="Домофон 123",
        )
        assert response.recipient_name == "Иван Иванов"
        assert response.delivery_city == "Москва"
        assert response.status == OrderStatus.IN_CART


class TestOrderModelAddressFields:
    """Tests for Order model address fields."""

    def test_order_model_has_address_attributes(self):
        """Test that Order model has all address attributes."""
        order = Order()
        assert hasattr(order, "recipient_name")
        assert hasattr(order, "recipient_phone")
        assert hasattr(order, "delivery_address")
        assert hasattr(order, "delivery_city")
        assert hasattr(order, "delivery_zip")
        assert hasattr(order, "delivery_notes")

    def test_order_to_entity_includes_address(self):
        """Test that Order.to_entity() includes address fields."""
        order = Order()
        order.id = 1
        order.amount = 100.00
        order.status = OrderStatus.PAYED
        order.recipient_name = "Иван Иванов"
        order.recipient_phone = "+79991234567"
        order.delivery_address = "ул. Примерная, д. 10"
        order.delivery_city = "Москва"
        order.delivery_zip = "123456"
        order.delivery_notes = "Домофон 123"

        entity = order.to_entity()

        assert entity.recipient_name == "Иван Иванов"
        assert entity.recipient_phone == "+79991234567"
        assert entity.delivery_address == "ул. Примерная, д. 10"
        assert entity.delivery_city == "Москва"
        assert entity.delivery_zip == "123456"
        assert entity.delivery_notes == "Домофон 123"
