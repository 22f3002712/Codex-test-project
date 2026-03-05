import logging
from datetime import date, timedelta

from backend.extensions import db
from backend.models.appointment import Appointment, AppointmentStatus
from backend.models.doctor import Doctor
from backend.models.doctor_availability import DoctorAvailability
from backend.models.treatment import Treatment
from backend.validators import validate_status_transition

logger = logging.getLogger(__name__)


def get_doctor_dashboard(user_id: int):
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        return {"message": "Doctor profile not found"}, 404

    today = date.today()
    upcoming_until = today + timedelta(days=7)

    todays_appointments = (
        Appointment.query.filter_by(doctor_id=doctor.id)
        .filter(Appointment.appointment_date == today)
        .order_by(Appointment.appointment_time.asc())
        .all()
    )

    upcoming_appointments = (
        Appointment.query.filter_by(doctor_id=doctor.id)
        .filter(Appointment.appointment_date > today)
        .filter(Appointment.appointment_date <= upcoming_until)
        .order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc())
        .all()
    )

    assigned_patients = (
        db.session.query(Appointment.patient_id)
        .filter(Appointment.doctor_id == doctor.id)
        .distinct()
        .all()
    )

    patient_ids = [record.patient_id for record in assigned_patients]
    patients = [
        {
            "id": appointment.patient.id,
            "name": appointment.patient.name,
            "email": appointment.patient.email,
            "phone": appointment.patient.phone,
        }
        for appointment in {
            appointment.patient_id: appointment
            for appointment in Appointment.query.filter(
                Appointment.doctor_id == doctor.id, Appointment.patient_id.in_(patient_ids)
            ).all()
        }.values()
    ]

    return {
        "today_appointments": [serialize_appointment(appointment) for appointment in todays_appointments],
        "upcoming_appointments": [
            serialize_appointment(appointment) for appointment in upcoming_appointments
        ],
        "assigned_patients": patients,
    }, 200


def complete_appointment(user_id: int, appointment_id: int):
    return update_appointment_status(user_id, appointment_id, AppointmentStatus.COMPLETED.value)


def cancel_appointment(user_id: int, appointment_id: int):
    return update_appointment_status(user_id, appointment_id, AppointmentStatus.CANCELLED.value)


def update_appointment_status(user_id: int, appointment_id: int, status: str):
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        return {"message": "Doctor profile not found"}, 404

    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor.id).first()
    if not appointment:
        return {"message": "Appointment not found"}, 404

    is_valid_transition, transition_error = validate_status_transition(appointment.status, status)
    if not is_valid_transition:
        logger.info(
            "Invalid status transition for appointment_id=%s: %s -> %s",
            appointment.id,
            appointment.status,
            status,
        )
        return {"message": transition_error}, 400

    appointment.status = status
    db.session.commit()

    return {
        "message": f"Appointment marked as {status.lower()}",
        "appointment": serialize_appointment(appointment),
    }, 200


def add_treatment(user_id: int, payload: dict):
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        return {"message": "Doctor profile not found"}, 404

    required_fields = ["appointment_id", "diagnosis"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return {"message": f"Missing fields: {', '.join(missing)}"}, 400

    appointment = Appointment.query.filter_by(
        id=payload["appointment_id"], doctor_id=doctor.id
    ).first()
    if not appointment:
        return {"message": "Appointment not found"}, 404

    treatment = Treatment(
        appointment_id=appointment.id,
        diagnosis=payload["diagnosis"],
        prescription=payload.get("prescription"),
        notes=payload.get("notes"),
    )

    db.session.add(treatment)
    db.session.commit()

    return {
        "message": "Treatment details added successfully",
        "treatment": {
            "id": treatment.id,
            "appointment_id": treatment.appointment_id,
            "diagnosis": treatment.diagnosis,
            "prescription": treatment.prescription,
            "notes": treatment.notes,
        },
    }, 201


def add_availability(user_id: int, payload: dict):
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        return {"message": "Doctor profile not found"}, 404

    availabilities = payload.get("availabilities")
    if not isinstance(availabilities, list) or len(availabilities) == 0:
        return {
            "message": "availabilities must be a non-empty list for the next 7 days"
        }, 400

    today = date.today()
    max_date = today + timedelta(days=7)

    created = []
    for item in availabilities:
        availability_date = item.get("date")
        available_slots = item.get("available_slots")

        if not availability_date or not available_slots:
            return {"message": "Each availability requires date and available_slots"}, 400

        try:
            parsed_date = date.fromisoformat(availability_date)
        except ValueError:
            return {"message": f"Invalid date format: {availability_date}"}, 400

        if parsed_date < today or parsed_date > max_date:
            return {
                "message": f"Availability date {availability_date} must be within next 7 days"
            }, 400

        existing = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id, date=parsed_date
        ).first()
        if existing:
            existing.available_slots = available_slots
            entry = existing
        else:
            entry = DoctorAvailability(
                doctor_id=doctor.id, date=parsed_date, available_slots=available_slots
            )
            db.session.add(entry)

        created.append(entry)

    db.session.commit()

    return {
        "message": "Doctor availability saved successfully",
        "availabilities": [
            {
                "id": availability.id,
                "date": availability.date.isoformat(),
                "available_slots": availability.available_slots,
            }
            for availability in created
        ],
    }, 200


def serialize_appointment(appointment: Appointment):
    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "patient_name": appointment.patient.name,
        "appointment_date": appointment.appointment_date.isoformat(),
        "appointment_time": appointment.appointment_time.isoformat(),
        "status": appointment.status,
    }
