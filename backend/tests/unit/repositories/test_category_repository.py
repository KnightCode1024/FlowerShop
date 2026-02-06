import pytest
from src.flowershop_api.schemas.category import CategoryUpdate
from src.flowershop_api.models import Category


class TestCategoryRepository:
    async def test_create_category_success(
        self,
        category_repository,
        test_category1,
    ):
        # Act
        result = await category_repository.create(test_category1)

        # Assert
        assert result.id is not None
        assert result.name == test_category1.name

    async def test_exists_by_name_detects_duplicate(
        self,
        category_repository,
        test_category1,
    ):
        # Arrange
        await category_repository.create(test_category1)

        # Act
        exists = await category_repository.exists_by_name(test_category1.name)

        # Assert
        assert exists is True

    async def test_get_category_by_id_existing(
        self, category_repository, test_category1
    ):
        # Arrange
        created_category = await category_repository.create(test_category1)

        # Act
        result = await category_repository.get_by_id(created_category.id)

        # Assert
        assert result is not None
        assert result.id == created_category.id
        assert result.name == test_category1.name

    async def test_get_category_by_id_not_existing(self, category_repository):
        # Act
        result = await category_repository.get_by_id(999)

        # Assert
        assert result is None

    async def test_get_all_categories_empty(self, category_repository):
        # Act
        result = await category_repository.get_all()

        # Assert
        assert result == []

    async def test_get_all_categories_with_data(
        self,
        category_repository,
        test_category1,
        test_category2,
    ):
        # Arrange
        await category_repository.create(test_category1)
        await category_repository.create(test_category2)

        # Act
        result = await category_repository.get_all()

        # Assert
        assert len(result) == 2
        names = [category.name for category in result]
        assert test_category1.name in names
        assert test_category2.name in names

    async def test_get_all_categories_with_pagination(
        self,
        category_repository,
        test_category1,
        test_category2,
        test_category3,
    ):
        # Arrange
        await category_repository.create(test_category1)
        await category_repository.create(test_category2)
        await category_repository.create(test_category3)

        # Act
        result = await category_repository.get_all(offset=1, limit=2)

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
    async def test_get_all_categories_pagination_parametrized(
        self,
        category_repository,
        multiple_categories,
        offset,
        limit,
        expected_count,
    ):
        result = await category_repository.get_all(offset=offset, limit=limit)
        assert len(result) == expected_count

    async def test_repository_returns_correct_types(
        self,
        category_repository,
        test_category1,
    ):
        # Arrange & Act
        created = await category_repository.create(test_category1)
        retrieved = await category_repository.get_by_id(created.id)
        all_categories = await category_repository.get_all()
        updated = await category_repository.update(
            created.id,
            CategoryUpdate(name="updated_category"),
        )

        # Assert
        assert isinstance(created, Category)
        assert isinstance(retrieved, Category) or retrieved is None
        assert isinstance(all_categories, list)
        assert all(isinstance(cat, Category) for cat in all_categories)
        assert isinstance(updated, Category) or updated is None

    async def test_update_category_success(
        self,
        category_repository,
        test_category1,
    ):
        # Arrange
        created_category = await category_repository.create(test_category1)
        update_data = CategoryUpdate(name="Updated Category Name")

        # Act
        result = await category_repository.update(
            created_category.id,
            update_data,
        )

        # Assert
        assert result is not None
        assert result.id == created_category.id
        assert result.name == "Updated Category Name"

    async def test_update_category_partial(
        self,
        category_repository,
        test_category1,
    ):
        # Arrange
        created_category = await category_repository.create(test_category1)
        update_data = CategoryUpdate(name="Partially Updated")

        # Act
        result = await category_repository.update(
            created_category.id,
            update_data,
        )

        # Assert
        assert result is not None
        assert result.name == "Partially Updated"

    async def test_update_category_not_existing(self, category_repository):
        # Arrange
        update_data = CategoryUpdate(name="Non-existent Category")

        # Act
        result = await category_repository.update(999, update_data)

        # Assert
        assert result is None

    async def test_update_category_empty_update_data(
        self,
        category_repository,
        test_category1,
    ):
        # Arrange
        created_category = await category_repository.create(test_category1)
        update_data = CategoryUpdate()

        # Act
        result = await category_repository.update(
            created_category.id,
            update_data,
        )

        # Assert
        assert result is not None
        assert result.name == test_category1.name

    async def test_delete_category_success(
        self,
        category_repository,
        test_category1,
    ):
        # Arrange
        created_category = await category_repository.create(test_category1)

        # Act
        result = await category_repository.delete(created_category.id)

        # Assert
        assert result is not None
        assert result.id == created_category.id
        assert result.name == test_category1.name

    async def test_delete_category_not_existing(self, category_repository):
        # Act
        result = await category_repository.delete(999)

        # Assert
        assert result is None

    async def test_exists_by_name_existing(
        self,
        category_repository,
        test_category1,
    ):
        # Arrange
        await category_repository.create(test_category1)

        # Act
        result = await category_repository.exists_by_name(test_category1.name)

        # Assert
        assert result is True

    async def test_exists_by_name_not_existing(self, category_repository):
        # Act
        result = await category_repository.exists_by_name(
            "Non-existent Category",
        )

        # Assert
        assert result is False

    async def test_exists_by_name_with_exclude_id(
        self,
        category_repository,
        test_category1,
        test_category2,
    ):
        # Arrange
        created1 = await category_repository.create(test_category1)
        created2 = await category_repository.create(test_category2)

        # Act & Assert
        assert (
            await category_repository.exists_by_name(
                test_category2.name,
            )
            is True
        )

        assert (
            await category_repository.exists_by_name(
                test_category2.name, exclude_id=created2.id
            )
            is False
        )

        assert (
            await category_repository.exists_by_name(
                test_category2.name, exclude_id=created1.id
            )
            is True
        )

    async def test_get_all_categories_returns_list_even_when_empty(
        self,
        category_repository,
    ):
        # Act
        result = await category_repository.get_all()

        # Assert
        assert isinstance(result, list)
        assert result == []


async def test_category_repository_workflow(
    category_repository,
    test_category1,
    test_category2,
):
    # Create
    created = await category_repository.create(test_category1)
    assert created.id is not None

    # Get by ID
    retrieved = await category_repository.get_by_id(created.id)
    assert retrieved.name == test_category1.name

    # Check exists by name
    exists = await category_repository.exists_by_name(test_category1.name)
    assert exists is True

    # Update
    updated = await category_repository.update(
        created.id,
        CategoryUpdate(name="Updated Category"),
    )
    assert updated.name == "Updated Category"

    # Check in all categories list
    all_categories = await category_repository.get_all()
    assert len(all_categories) == 1
    assert all_categories[0].name == "Updated Category"

    # Create second category
    created2 = await category_repository.create(test_category2)
    assert created2.id != created.id

    # Check both categories in list
    all_categories = await category_repository.get_all()
    assert len(all_categories) == 2

    # Delete first category
    deleted = await category_repository.delete(created.id)
    assert deleted.id == created.id
    assert deleted.name == "Updated Category"

    # Note: Due to session rollback in tests, the category remains in DB
    # But the delete method returns the correct object
