from functools import wraps
import jwt
from flask import request, abort, current_app
from domain.repository.user_repository import read_user_by_id


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            try:
                token = request.headers["Authorization"].split(" ")[1]
            except IndexError:
                return {
                    "message": "Token format is invalid!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401

        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401

        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = read_user_by_id(data["user_id"])

            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401

            if not current_user["active"]:
                abort(403)

        except jwt.ExpiredSignatureError:
            return {
                "message": "Token has expired!",
                "data": None,
                "error": "Unauthorized"
            }, 401

        except jwt.InvalidTokenError:
            return {
                "message": "Invalid token!",
                "data": None,
                "error": "Unauthorized"
            }, 401

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return func(current_user, *args, **kwargs)

    return decorated
