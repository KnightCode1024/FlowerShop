import pytest

from utils.strings import is_valid_email


@pytest.mark.parametrize("email, result", [("ivani@vanov1234gmail.com", True),
                                           ("ivani@#$@$vanov1234gmail.com", False),
                                           ("@dadas", False),
                                           ("kduadad@@@@..com", False),
                                           ("ivanivanov1234@gmail.com", True),
                                           ("#@!#$!@$$!$@mail.com", False)])
def test_is_valid_email(email: str, result: bool):
    assert is_valid_email(email) is result
