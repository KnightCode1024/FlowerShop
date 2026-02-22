import random
import secrets
import string
from string import *


def generate_random_token(length: int = 16):
    return "".join(random.sample(hexdigits + digits, k=length))


def generate_random_promo(length: int = 5):
    return generate_random_token(length)


def generate_random_password(length: int = 16):
    rand_pass_list = random.sample(ascii_letters, k=length)

    rand_pass_list.append(random.choice(["@", "!", "+", "="]))

    rand_pass_list.append(str(random.randint(1, 9)))

    return "".join(rand_pass_list)


def make_valid_password(min_length=12):
    specials = '!@#$%^&*(),.?":{}|<>'
    while True:
        pwd_chars = (
            secrets.choice(string.ascii_uppercase) +
            secrets.choice(string.ascii_lowercase) +
            secrets.choice(string.digits) +
            secrets.choice(specials)
        )
        while len(pwd_chars) < min_length:
            pwd_chars += secrets.choice(string.ascii_letters + string.digits + specials)
        pwd = ''.join(secrets.choice(pwd_chars) for _ in range(min_length))
        if (any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd)
                and any(c in specials for c in pwd)
                and len(pwd) >= min_length):
            return pwd