import hashlib
import re
import string

import jwt
from cryptography.fernet import Fernet
from django.contrib.auth.models import User
from jwt import InvalidSignatureError


def get_sha3_256_hash(value: str):
    _hash = hashlib.sha3_256()
    _hash.update(value.encode())
    return _hash.hexdigest()


class RandomLessFernet(Fernet):
    def encrypt(self, data):
        return self._encrypt_from_parts(data, 1578640759, b"\xad\r\xc9\xba\xae'\x86\x08\x9b\xe8\xe00[9Ep")


CRYPTO_KEY = b'Z8HiBW9BqqmG25lf0SxvT1TJNZKNUniOir5hbJWrCj0='    # should get from env.


def encrypt(value: str):
    if not isinstance(value, bytes):
        value = str(value).encode()
    return RandomLessFernet(CRYPTO_KEY).encrypt(value).decode()


def decrypt(value: bytes):
    if not isinstance(value, bytes):
        value = str(value).encode()
    return RandomLessFernet(CRYPTO_KEY).decrypt(value).decode()


JWT_KEY = 'TH1fxMv_H3GBEx2oRb2V7caHe6d1SHUB8UW5F5QKnqk'    # should get from env.


def make_jwt(user: User):
    return jwt.encode({'id': user.id}, JWT_KEY, algorithm='HS256')


def decode_jwt(token: str):
    try:
        return jwt.decode(token.encode(), JWT_KEY, algorithms='HS256')
    except InvalidSignatureError:
        pass
    return ''


def check_username(username):
    size = len(username)
    if size < 5:
        return 0, "Short id"
    elif size > 20:
        return 0, "Long id"
    if any(check in username for check in string.ascii_uppercase):
        return 0, "Uppercase id"
    if any(check in username for check in ' !@#$%^&*()-_+=`~;:/?.>,<\\|[]{}'):
        return 0, "special characters id"
    return 1, "success"


def check_password(password):
    size = len(password)
    if size < 8:
        return 0, "Short pw"
    elif size > 16:
        return 0, "Long pw"
    else:
        return 1, "success"


def check_phone(phone):
    regex = re.compile(r'^\d{3}-?(\d{4}|\d{3})-?\d{4}$')
    check = regex.search(phone)
    if check:
        return 1, "success"
    else:
        return 0, "Invalid number"
