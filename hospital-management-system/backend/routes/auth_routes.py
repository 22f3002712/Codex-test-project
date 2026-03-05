from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from backend.extensions import db
from backend.models.patient import Patient
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

    required_fields = ["username", "email", "password", "name"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(username=payload["username"]).first():
        return jsonify({"message": "Username already exists"}), 409

    if Patient.query.filter_by(email=payload["email"]).first():
        return jsonify({"message": "Patient email already exists"}), 409

    user = User(
        username=payload["username"],
        role=Role.PATIENT.value,
    )
    user.set_password(payload["password"])

    patient = Patient(
        user=user,
        name=payload["name"],
        email=payload["email"],
        phone=payload.get("phone"),
        address=payload.get("address"),
        date_of_birth=payload.get("date_of_birth"),
    )

    db.session.add_all([user, patient])
    db.session.commit()

    return jsonify({"message": "Patient registered successfully"}), 201
