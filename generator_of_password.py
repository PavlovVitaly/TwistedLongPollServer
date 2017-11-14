import random
from string import digits, ascii_letters


def password_generator(num):
    valid_values = list(digits + ascii_letters)

    while True:
        result = (valid_values[random.randint(0, len(valid_values) - 1)] for i in range(num))
        yield ''.join(result)
