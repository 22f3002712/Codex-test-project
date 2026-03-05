from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request



def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return jsonify({"message": "Forbidden: insufficient permissions"}), 403
            return func(*args, **kwargs)

        return wrapper

    return decorator
