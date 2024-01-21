import string
import random

from django.conf import settings
from jwt import encode, decode


def generate_test_token(type_of_tokens, day=None, course_id=None):
    characters = string.ascii_uppercase + string.digits
    generate_code = "".join(random.choice(characters) for _ in range(6))

    if type_of_tokens == "course":
        return {"type": "course", "course_id": course_id, "code": generate_code}

    payload = {"type": "test", "day": day}
    jwt_token = encode(payload, settings.SECRET_KEY)
    return {"generated_code": generate_code, "token": jwt_token}


def decode_token(token):
    data = decode(token, settings.SECRET_KEY)
    return data
