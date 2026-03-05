from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models.user import User
from backend.utils.auth import admin_required, doctor_required, patient_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("/admin")
@admin_required
def admin_dashboard():
    return jsonify({"message": "Welcome to Admin dashboard"})


@dashboard_bp.get("/doctor")
@doctor_required
def doctor_dashboard():
    return jsonify({"message": "Welcome to Doctor dashboard"})


@dashboard_bp.get("/patient")
@patient_required
def patient_dashboard():
    return jsonify({"message": "Welcome to Patient dashboard"})


@dashboard_bp.get("/me")
@jwt_required()
def current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
    )
