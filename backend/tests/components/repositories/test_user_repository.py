import pytest
from sqlalchemy.exc import IntegrityError

from src.models import RoleEnum, User
from src.schemas.user import UserCreate, UserUpdate


class TestUserRepository:
    async def test_create_user_success(self, user_repository, test_user1):
        # Act
        result = await user_repository.create(test_user1)

        # Assert
        assert result.id is not None
        assert result.email == test_user1.email
        assert result.username == test_user1.username
        assert result.password == test_user1.password
        assert result.role == RoleEnum.USER

    async def test_create_user_duplicate_email(
        self,
        user_repository,
        test_user1,
    ):
        # Arrange
        await user_repository.create(test_user1)

        # Act & Assert
        with pytest.raises(IntegrityError):
            await user_repository.create(test_user1)

    async def test_get_user_existing(self, user_repository, test_user1):
        # Arrange
        created_user = await user_repository.create(test_user1)

        # Act
        result = await user_repository.get(created_user.id)

        # Assert
        assert result is not None
        assert result.id == created_user.id
        assert result.email == test_user1.email
        assert result.username == test_user1.username

    async def test_get_user_not_existing(self, user_repository):
        # Act
        result = await user_repository.get(999)

        # Assert
        assert result is None

    async def test_get_all_users_empty(self, user_repository):
        # Act
        result = await user_repository.get_all()

        # Assert
        assert result == []

    async def test_get_all_users_with_data(
        self, user_repository, test_user1, test_user2
    ):
        # Arrange
        await user_repository.create(test_user1)
        await user_repository.create(test_user2)

        # Act
        result = await user_repository.get_all()

        # Assert
        assert len(result) == 2
        emails = [user.email for user in result]
        assert test_user1.email in emails
        assert test_user2.email in emails

    async def test_get_all_users_with_pagination(
        self, user_repository, test_user1, test_user2, test_user3
    ):
        # Arrange
        await user_repository.create(test_user1)
        await user_repository.create(test_user2)
        await user_repository.create(test_user3)

        # Act
        result = await user_repository.get_all(offset=1, limit=2)

        # Assert
        assert len(result) == 2

    async def test_update_user_success(self, user_repository, test_user1):
        # Arrange
        created_user = await user_repository.create(test_user1)
        update_data = UserUpdate(
            username="updated_username", email="updated@example.com"
        )

        # Act
        result = await user_repository.update(created_user.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_user.id
        assert result.username == "updated_username"
        assert result.email == "updated@example.com"
        assert result.password == test_user1.password  # Пароль не изменился

    async def test_update_user_partial(self, user_repository, test_user1):
        # Arrange
        created_user = await user_repository.create(test_user1)
        update_data = UserUpdate(username="only_username")

        # Act
        result = await user_repository.update(created_user.id, update_data)

        # Assert
        assert result is not None
        assert result.username == "only_username"
        assert result.email == test_user1.email  # Email не изменился

    async def test_update_user_not_existing(self, user_repository):
        # Arrange
        update_data = UserUpdate(username="test")

        # Act
        result = await user_repository.update(999, update_data)

        # Assert
        assert result is None

    async def test_get_user_by_email_existing(
        self,
        user_repository,
        test_user1,
    ):
        # Arrange
        await user_repository.create(test_user1)

        # Act
        result = await user_repository.get_user_by_email(test_user1.email)

        # Assert
        assert result is not None
        assert result.email == test_user1.email
        assert result.username == test_user1.username

    async def test_get_user_by_email_not_existing(self, user_repository):
        # Act
        result = await user_repository.get_user_by_email(
            "nonexistent@example.com",
        )

        # Assert
        assert result is None

    async def test_get_user_by_email_case_sensitive(
        self,
        user_repository,
        test_user1,
    ):
        # Arrange
        await user_repository.create(test_user1)

        # Act
        result = await user_repository.get_user_by_email(
            test_user1.email.upper(),
        )

        # Assert
        assert result is None

    @pytest.mark.parametrize(
        "offset,limit,expected_count",
        [
            (0, 10, 3),
            (1, 2, 2),
            (2, 10, 1),
            (10, 10, 0),
        ],
    )
    async def test_get_all_users_pagination_parametrized(
        self, user_repository, multiple_users, offset, limit, expected_count
    ):
        result = await user_repository.get_all(offset=offset, limit=limit)
        assert len(result) == expected_count

    async def test_repository_returns_correct_types(
        self,
        user_repository,
        test_user1,
    ):
        # Arrange & Act
        created = await user_repository.create(test_user1)
        retrieved = await user_repository.get(created.id)
        all_users = await user_repository.get_all()
        by_email = await user_repository.get_user_by_email(test_user1.email)
        updated = await user_repository.update(
            created.id,
            UserUpdate(username="test"),
        )

        # Assert
        assert isinstance(created, User)
        assert isinstance(retrieved, User) or retrieved is None
        assert isinstance(all_users, list)
        assert all(isinstance(user, User) for user in all_users)
        assert isinstance(by_email, User) or by_email is None
        assert isinstance(updated, User) or updated is None

    async def test_create_user_with_none_role_defaults_to_user(
        self,
        user_repository,
    ):
        # Arrange
        user_data = UserCreate(
            email="default_role@example.com",
            username="default_role",
            password="password123",
        )

        # Act
        result = await user_repository.create(user_data)

        # Assert
        assert result.role == RoleEnum.USER

    async def test_update_user_empty_update_data(
        self,
        user_repository,
        test_user1,
    ):
        # Arrange
        created_user = await user_repository.create(test_user1)
        update_data = UserUpdate()

        # Act
        result = await user_repository.update(created_user.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_user.id
        assert result.username == test_user1.username  # Данные не изменились
        assert result.email == test_user1.email

    async def test_get_all_users_returns_list_even_when_empty(
        self,
        user_repository,
    ):
        # Act
        result = await user_repository.get_all()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0


async def test_user_repository_workflow(
    user_repository,
    test_user1,
    test_user2,
):
    created = await user_repository.create(test_user1)
    assert created.id is not None

    retrieved = await user_repository.get(created.id)
    assert retrieved.email == test_user1.email

    by_email = await user_repository.get_user_by_email(test_user1.email)
    assert by_email.id == created.id

    updated = await user_repository.update(
        created.id,
        UserUpdate(username="new_name"),
    )
    assert updated.username == "new_name"

    all_users = await user_repository.get_all()
    assert len(all_users) == 1
    assert all_users[0].username == "new_name"

    created2 = await user_repository.create(test_user2)
    assert created2.id != created.id

    all_users = await user_repository.get_all()
    assert len(all_users) == 2
    emails = {user.email for user in all_users}
    assert test_user1.email in emails
    assert test_user2.email in emails
