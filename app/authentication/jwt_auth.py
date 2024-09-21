import binascii
import hashlib
import os
import time
from datetime import datetime, timezone

import jwt
from flask import current_app
from flask_restx import Api
from werkzeug.security import check_password_hash

from gateways.databases.connection import session

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback_secret_key')


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return salt + pwdhash


def verify_pass(provided_password, stored_password):
    return check_password_hash(provided_password, stored_password)


def generate_api_token(user_id):
    now = int(datetime.now(timezone.utc).timestamp())
    api_token = jwt.encode(
        {"user_id": user_id,
         "init_date": now},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return api_token


def update_user_api_token(user):
    token = generate_api_token(user.id)
    user.api_token = token
    user.api_token_ts = int(time.time())
    session.commit()
    return token


def get_api(blueprint):
    api = Api(blueprint, version='1.0', title='Seller', description='Documentação API para MVP', doc="/docs")
    return api
