import logging
import os
import random
import string


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '../../static/assets')

    SECRET_KEY = os.getenv('JWT_SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True


config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}

