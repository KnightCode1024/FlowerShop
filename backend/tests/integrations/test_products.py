import random
import pytest

from schemas.category import CategoryResponse, CategoryCreate
from schemas.product import CreateProductRequest, ProductResponse


@pytest.mark.asyncio
async def test_success_create_product(created_admin_client):
    category_data = CategoryCreate(
        name=f"category_name_{random.randint(1, 1000)}"
    )
    response1 = await created_admin_client.post(
        "/categories/",
        json=category_data.model_dump(),
    )
    category = CategoryResponse(**response1.json())

    product_data = CreateProductRequest(
        name=f'product_{random.randint(1, 10000)}',
        description=f"desc_{random.randint(1, 10000)}",
        price=random.uniform(100.00, 1000.00),
        in_stock=random.choice([True, False]),
        category_id=category.id
    )

    response2 = await created_admin_client.post(
        "/products/",
        json={"product_data": product_data.json()},
        files=[("images", ("photo_1.png", open("media/photo_1.png", "rb"), "image/png"))]
    )

    product = ProductResponse(**response2.json())

    assert product.category_id == product_data.category_id
    assert product.name == product_data.name
    assert product.description == product_data.description
    assert product.in_stock == product_data.in_stock
    assert product.price == product_data.price
