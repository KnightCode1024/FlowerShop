import bcrypt

from utils.jwt_utils import hash_password, validate_password
from utils.strings import make_valid_password


def test_create_is_valid_hash_password():
    gen_password = make_valid_password()
    hashed_password = hash_password(gen_password)

    assert validate_password(gen_password, hashed_password) is True


def test_is_not_valid_hashed_password():
    gen_password = make_valid_password()
    hashed_password = hash_password(gen_password) + "123"

    assert validate_password(gen_password, hashed_password) is False
