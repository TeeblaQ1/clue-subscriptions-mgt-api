from flask import request
from functools import wraps
from app.utils.auth_utils import AuthUtils
from app.utils.response import make_response

def jwt_required(f):
    """
    Decorator to check if the user is authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return make_response(message="Unauthorized", status_code=401)
        if not auth_header.startswith("Bearer "):
            return make_response(message="Invalid token", status_code=401)
        token = auth_header.split(" ", 1)[1]
        user = AuthUtils.get_user_from_token(token)
        if not user:
            return make_response(message="Invalid token", status_code=401)
        return f(user.id, *args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to check if the user is authenticated and is an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return make_response(message="Unauthorized", status_code=401)
        if not auth_header.startswith("Bearer "):
            return make_response(message="Invalid token", status_code=401)
        token = auth_header.split(" ", 1)[1]
        user = AuthUtils.get_user_from_token(token)
        if not user:
            return make_response(message="Invalid token", status_code=401)
        if not user.is_admin:
            return make_response(message="Unauthorized", status_code=401)
        return f(user.id, *args, **kwargs)
    return decorated_function
