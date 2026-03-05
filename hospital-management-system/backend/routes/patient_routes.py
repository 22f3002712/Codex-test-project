from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from backend.services.patient_service import (
    book_appointment,
    cancel_patient_appointment,
    get_patient_dashboard,
    get_treatment_history,
    reschedule_appointment,
    search_doctors,
)
from backend.utils.auth import patient_required

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


@patient_bp.get("/dashboard")
@patient_required
def patient_dashboard():
    user_id = int(get_jwt_identity())
    result, status_code = get_patient_dashboard(user_id)
    return jsonify(result), status_code


@patient_bp.get("/search")
@patient_required
def patient_search_doctors():
    doctor_name = request.args.get("doctor_name")
    specialization = request.args.get("specialization")

    result, status_code = search_doctors(doctor_name=doctor_name, specialization=specialization)
    return jsonify(result), status_code


@patient_bp.post("/appointments")
@patient_required
def patient_book_appointment():
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    result, status_code = book_appointment(user_id, payload)
    return jsonify(result), status_code


@patient_bp.put("/appointments/<int:appointment_id>")
@patient_required
def patient_reschedule_appointment(appointment_id: int):
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    result, status_code = reschedule_appointment(user_id, appointment_id, payload)
    return jsonify(result), status_code


@patient_bp.delete("/appointments/<int:appointment_id>")
@patient_required
def patient_cancel_appointment(appointment_id: int):
    user_id = int(get_jwt_identity())
    result, status_code = cancel_patient_appointment(user_id, appointment_id)
    return jsonify(result), status_code


@patient_bp.get("/treatments")
@patient_required
def patient_treatments():
    user_id = int(get_jwt_identity())
    result, status_code = get_treatment_history(user_id)
    return jsonify(result), status_code
