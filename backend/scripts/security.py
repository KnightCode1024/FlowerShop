import secrets


def generate_secret_key():
    secret_key = secrets.token_hex(32)
    print(secret_key)


generate_secret_key()