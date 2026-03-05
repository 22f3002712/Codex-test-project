from flask import Blueprint, jsonify, request

from backend.services.auth_service import login_user, register_patient

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    auth_data = login_user(username, password)
    if not auth_data:
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify(auth_data), 200


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    result, status_code = register_patient(payload)
    return jsonify(result), status_code
