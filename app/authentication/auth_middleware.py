import os

import jwt
import logging
from functools import wraps
from flask import request, abort, current_app, jsonify

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback_secret_key')
logger = logging.getLogger(__name__)


def create_error_response(message, error_type="Unauthorized", status_code=401):
    return {
        "message": message,
        "data": None,
        "error": error_type
    }, status_code


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # 'Bearer <token>'

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['sub']  # ou o campo que contém o ID do usuário
        except Exception as e:
            return jsonify({'message': 'Invalid token!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated