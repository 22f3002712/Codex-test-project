from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from backend.services.doctor_service import (
    add_availability,
    add_treatment,
    cancel_appointment,
    complete_appointment,
    get_doctor_dashboard,
)
from backend.utils.auth import doctor_required

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


@doctor_bp.get("/dashboard")
@doctor_required
def doctor_dashboard():
    user_id = int(get_jwt_identity())
    result, status_code = get_doctor_dashboard(user_id)
    return jsonify(result), status_code


@doctor_bp.post("/appointment/<int:appointment_id>/complete")
@doctor_required
def mark_appointment_completed(appointment_id: int):
    user_id = int(get_jwt_identity())
    result, status_code = complete_appointment(user_id, appointment_id)
    return jsonify(result), status_code


@doctor_bp.post("/appointment/<int:appointment_id>/cancel")
@doctor_required
def mark_appointment_cancelled(appointment_id: int):
    user_id = int(get_jwt_identity())
    result, status_code = cancel_appointment(user_id, appointment_id)
    return jsonify(result), status_code


@doctor_bp.post("/treatment")
@doctor_required
def create_treatment():
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    result, status_code = add_treatment(user_id, payload)
    return jsonify(result), status_code


@doctor_bp.post("/availability")
@doctor_required
def create_availability():
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    result, status_code = add_availability(user_id, payload)
    return jsonify(result), status_code
