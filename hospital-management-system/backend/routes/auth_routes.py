from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from backend.extensions import db
from backend.models.user import Role, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"access_token": token, "role": user.role}), 200


@auth_bp.post("/register")
def register_patient():
    payload = request.get_json(silent=True) or {}

    required_fields = ["username", "email", "password"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter(
        (User.username == payload["username"]) | (User.email == payload["email"])
    ).first():
        return jsonify({"message": "Username or email already exists"}), 409

    user = User(
        username=payload["username"],
        email=payload["email"],
        role=Role.PATIENT.value,
    )
    user.set_password(payload["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Patient registered successfully"}), 201
