import random
import string
from string import hexdigits


def generate_random_token(length: int = 16):
    return "".join(random.sample(hexdigits + string.digits, k=length))


def generate_random_promo(length: int = 5):
    return generate_random_token(length)
