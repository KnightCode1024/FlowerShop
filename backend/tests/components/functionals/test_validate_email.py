from utils.strings import is_valid_email


def test_is_valid_email_success():
    email = "ivanivanov1234@gmail.com"

    assert is_valid_email(email) is True


def test_is_valid_email_failed():
    email1 = "ivani@vanov1234gmail.com@"
    email2 = "ivani@#$@$vanov1234gmail.com"
    email3 = "@dadas"
    email4 = "kduadad@@@@..com"

    assert is_valid_email(email1) is False
    assert is_valid_email(email2) is False
    assert is_valid_email(email3) is False
    assert is_valid_email(email4) is False
