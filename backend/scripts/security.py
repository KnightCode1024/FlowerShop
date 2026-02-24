import secrets

import pyotp


def generate_secret_key():
    return secrets.token_hex(32)


def generate_base32_key():
    return pyotp.random_base32()


print(f"SECRET_KEY = {generate_secret_key()}")
print(f"OTP_SECRET = {generate_base32_key()}")
