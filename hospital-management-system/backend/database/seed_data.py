"""Utilities for seeding the SQLite database with repeatable sample data."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from backend.models.appointment import Appointment
from backend.models.department import Department
from backend.models.doctor import Doctor
from backend.models.patient import Patient
from backend.models.treatment import Treatment
from backend.models.user import Role, User


# Resolve the repository root from this file location once, then reuse it.
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLE_DATA_PATH = REPO_ROOT / "sample_data" / "seed_data.json"


def _load_seed_payload(data_path: str | Path | None = None) -> dict:
    """Load the JSON sample payload used to create demo records."""
    target_path = Path(data_path) if data_path else DEFAULT_SAMPLE_DATA_PATH
    with target_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def seed_database(db, data_path: str | Path | None = None) -> dict:
    """Insert seed records while keeping the operation idempotent by unique keys."""
    payload = _load_seed_payload(data_path)

    departments_by_name = {}
    for department_payload in payload.get("departments", []):
        department = Department.query.filter_by(name=department_payload["name"]).first()
        if not department:
            department = Department(**department_payload)
            db.session.add(department)
        departments_by_name[department_payload["name"]] = department

    # Flush first so new departments get IDs before doctor creation.
    db.session.flush()

    doctors_by_username = {}
    for doctor_payload in payload.get("doctors", []):
        user = User.query.filter_by(username=doctor_payload["username"]).first()
        if not user:
            user = User(username=doctor_payload["username"], role=Role.DOCTOR.value)
            user.set_password(doctor_payload["password"])
            db.session.add(user)
            db.session.flush()

        department = departments_by_name[doctor_payload["department"]]
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if not doctor:
            doctor = Doctor(
                user_id=user.id,
                name=doctor_payload["name"],
                specialization=doctor_payload["specialization"],
                department_id=department.id,
                is_active=True,
                is_blacklisted=False,
            )
            db.session.add(doctor)

        doctors_by_username[doctor_payload["username"]] = doctor

    db.session.flush()

    patients_by_username = {}
    for patient_payload in payload.get("patients", []):
        user = User.query.filter_by(username=patient_payload["username"]).first()
        if not user:
            user = User(username=patient_payload["username"], role=Role.PATIENT.value)
            user.set_password(patient_payload["password"])
            db.session.add(user)
            db.session.flush()

        patient = Patient.query.filter_by(user_id=user.id).first()
        if not patient:
            patient = Patient(
                user_id=user.id,
                name=patient_payload["name"],
                email=patient_payload["email"],
                phone=patient_payload.get("phone"),
                address=patient_payload.get("address"),
            )
            db.session.add(patient)

        patients_by_username[patient_payload["username"]] = patient

    db.session.flush()

    for appointment_payload in payload.get("appointments", []):
        patient = patients_by_username[appointment_payload["patient_username"]]
        doctor = doctors_by_username[appointment_payload["doctor_username"]]

        appointment_date = datetime.strptime(appointment_payload["appointment_date"], "%Y-%m-%d").date()
        appointment_time = datetime.strptime(appointment_payload["appointment_time"], "%H:%M").time()

        appointment = Appointment.query.filter_by(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        ).first()

        if not appointment:
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=appointment_payload.get("status", "Booked"),
            )
            db.session.add(appointment)
            db.session.flush()

        treatment_payload = appointment_payload.get("treatment")
        if treatment_payload and not Treatment.query.filter_by(appointment_id=appointment.id).first():
            db.session.add(
                Treatment(
                    appointment_id=appointment.id,
                    diagnosis=treatment_payload["diagnosis"],
                    prescription=treatment_payload.get("prescription"),
                    notes=treatment_payload.get("notes"),
                )
            )

    db.session.commit()

    return {
        "departments": Department.query.count(),
        "doctors": Doctor.query.count(),
        "patients": Patient.query.count(),
        "appointments": Appointment.query.count(),
        "treatments": Treatment.query.count(),
    }
