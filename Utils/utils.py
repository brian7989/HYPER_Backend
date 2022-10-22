import string
import random


def _generate_random_string(size, chars=string.ascii_uppercase + string.digits) -> str:
    return ''.join(random.choice(chars) for _ in range(size))


def generate_user_id() -> str:
    return _generate_random_string(size=12)


def generate_job_id() -> str:
    return _generate_random_string(size=8)


def generate_auth_id() -> str:
    return _generate_random_string(size=6)
