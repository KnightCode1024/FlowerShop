import pytest

from schemas.category import CategoryCreate, CategoryResponse
from schemas.invoice import InvoiceCreateRequest, InvoiceResponse
from schemas.order import OrderCreate, OrderCreateRequest, CartItem, OrderResponse


@pytest.mark.asyncio
async def test_create_category(created_admin_client):
    category = CategoryCreate(name="Розы")
    response = await created_admin_client.post("/categories/", json=category)

    assert response.status_code == 200

    category_created = CategoryResponse(**response.json())

    assert category_created.name == category.name
