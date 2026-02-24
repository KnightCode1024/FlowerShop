import pytest

from schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate, CategoriesListResponse
from schemas.invoice import InvoiceCreateRequest, InvoiceResponse
from schemas.order import OrderCreate, OrderCreateRequest, CartItem, OrderResponse


@pytest.mark.asyncio
async def test_create_category(created_admin_client):
    category = CategoryCreate(name="Розы")
    response = await created_admin_client.post("/categories/", json=category)

    assert response.status_code == 200

    category_created = CategoryResponse(**response.json())

    assert category_created.name == category.name

    return category


@pytest.mark.asyncio
async def test_delete_category(created_admin_client):
    category = await test_create_category(created_admin_client)

    response = await created_admin_client.delete(f"/categories/{category.id}")

    assert response.status_code == 200
    assert response.json() == None


@pytest.mark.asyncio
async def test_update_category(created_admin_client):
    category_data = CategoryUpdate(name="Архидеи")

    category = await test_create_category(created_admin_client)

    response = await created_admin_client.put(f"/categories/{category.id}", json=category_data.json())

    category_updated = CategoryResponse(**response.json())

    assert category_updated.name == category_data.name


@pytest.mark.asyncio
async def test_get_all_categories(created_admin_client):
    cats: list[CategoryResponse] = []
    for i in range(3):
        category = CategoryCreate(name=f"Розы{i}")
        response = await created_admin_client.post("/categories/", json=category)

        assert response.status_code == 200
        category_created = CategoryResponse(**response.json())

        assert category_created.name == category.name
        cats.append(category_created)

    response2 = await created_admin_client.get("/categories/")
    categories: list[CategoriesListResponse] = [CategoriesListResponse(**i) for i in response2.json()]

    assert sorted([i.name for i in categories]) == sorted([i.name for i in cats])


@pytest.mark.asyncio
async def test_get_one_category(created_admin_client):
    category = CategoryCreate(name=f"Розы")
    response = await created_admin_client.post("/categories/", json=category)

    assert response.status_code == 200
    category_created = CategoryResponse(**response.json())

    response2 = await created_admin_client.get(f"/categories/{category_created.id}")
    category_get = CategoryResponse(**response2.json())

    assert category_created.name == category_get.name
    assert category_get.id == category_created.id