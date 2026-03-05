from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models.user import User
from backend.utils.auth import role_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("/admin")
@role_required("admin")
def admin_dashboard():
    return jsonify({"message": "Welcome to Admin dashboard"})


@dashboard_bp.get("/doctor")
@role_required("doctor")
def doctor_dashboard():
    return jsonify({"message": "Welcome to Doctor dashboard"})


@dashboard_bp.get("/patient")
@role_required("patient")
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
