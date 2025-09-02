
import os

import bcrypt
from django.conf import settings


def get_apple_wallet_pass_url(email: str) -> str:
    email = email.encode()
    salt = os.environ.get("APPLE_WALLET_SALT").encode()
    hashed_email = bcrypt.hashpw(email, salt)

    #Make hash alphanumeric so that it can be used as a filename
    alphanumeric_hash = ''.join(char for char in hashed_email.decode() if char.isalnum())

    return settings.APPLE_WALLET_S3_BUCKET_URL + "/" + alphanumeric_hash + ".pkpass"
