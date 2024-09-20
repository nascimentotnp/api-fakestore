from datetime import datetime, timezone
from functools import wraps

import jwt
from flask import request, current_app

from domain.repository.user_repository import read_user_by_id


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        else:
            return {
                       'message': 'Token is missing',
                       'data': None,
                       'success': False
                   }, 403
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = read_user_by_id(data['user_id'])
            if current_user is None:
                return {
                           'message': 'Invalid token',
                           'data': None,
                           'success': False
                       }, 403
            now = int(datetime.now(timezone.utc).timestamp())
            init_date = data['init_date']

        except Exception as e:
            return {
                       'message': str(e),
                       'data': None,
                       'success': False
                   }, 500
        return func(*args, **kwargs)

    return decorated
