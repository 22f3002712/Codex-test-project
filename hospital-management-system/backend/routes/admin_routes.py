from flask import Blueprint, jsonify, request

from backend.services.admin_service import (
    blacklist_doctor,
    blacklist_patient,
    create_doctor,
    delete_doctor,
    get_all_appointments,
    get_dashboard_metrics,
    search_records,
    update_doctor,
)
from backend.utils.auth import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/dashboard")
@admin_required
def admin_dashboard():
    result, status_code = get_dashboard_metrics()
    return jsonify(result), status_code


@admin_bp.post("/doctors")
@admin_required
def add_doctor():
    payload = request.get_json(silent=True) or {}
    result, status_code = create_doctor(payload)
    return jsonify(result), status_code


@admin_bp.put("/doctors/<int:doctor_id>")
@admin_required
def edit_doctor(doctor_id: int):
    payload = request.get_json(silent=True) or {}
    result, status_code = update_doctor(doctor_id, payload)
    return jsonify(result), status_code


@admin_bp.delete("/doctors/<int:doctor_id>")
@admin_required
def remove_doctor(doctor_id: int):
    result, status_code = delete_doctor(doctor_id)
    return jsonify(result), status_code


@admin_bp.put("/doctors/<int:doctor_id>/blacklist")
@admin_required
def block_doctor(doctor_id: int):
    result, status_code = blacklist_doctor(doctor_id)
    return jsonify(result), status_code


@admin_bp.put("/patients/<int:patient_id>/blacklist")
@admin_required
def block_patient(patient_id: int):
    result, status_code = blacklist_patient(patient_id)
    return jsonify(result), status_code


@admin_bp.get("/search")
@admin_required
def search():
    result, status_code = search_records(
        doctor_name=request.args.get("doctor_name"),
        specialization=request.args.get("specialization"),
        patient_name=request.args.get("patient_name"),
    )
    return jsonify(result), status_code


@admin_bp.get("/appointments")
@admin_required
def appointments():
    result, status_code = get_all_appointments()
    return jsonify(result), status_code
