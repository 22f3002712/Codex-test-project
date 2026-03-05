from datetime import date, datetime

from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models.appointment import Appointment, AppointmentStatus
from backend.models.department import Department
from backend.models.doctor import Doctor
from backend.models.doctor_availability import DoctorAvailability
from backend.models.patient import Patient
from backend.models.treatment import Treatment


def get_patient_dashboard(user_id: int):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return {"message": "Patient profile not found"}, 404

    today = date.today()

    departments = Department.query.order_by(Department.name.asc()).all()
    doctors = (
        Doctor.query.filter_by(is_active=True, is_blacklisted=False)
        .order_by(Doctor.name.asc())
        .all()
    )

    upcoming = (
        Appointment.query.filter_by(patient_id=patient.id)
        .filter(Appointment.appointment_date >= today)
        .order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc())
        .all()
    )

    history = (
        Appointment.query.filter_by(patient_id=patient.id)
        .filter(Appointment.appointment_date < today)
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        .all()
    )

    return {
        "available_departments": [serialize_department(department) for department in departments],
        "available_doctors": [serialize_doctor(doctor) for doctor in doctors],
        "upcoming_appointments": [serialize_appointment(appointment) for appointment in upcoming],
        "appointment_history": [serialize_appointment(appointment) for appointment in history],
    }, 200


def search_doctors(doctor_name=None, specialization=None):
    if not doctor_name and not specialization:
        return {"message": "Provide one query parameter: doctor_name or specialization"}, 400

    query = Doctor.query.filter_by(is_active=True, is_blacklisted=False)

    if doctor_name:
        query = query.filter(Doctor.name.ilike(f"%{doctor_name}%"))

    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))

    doctors = query.order_by(Doctor.name.asc()).all()

    return {"doctors": [serialize_doctor(doctor) for doctor in doctors]}, 200


def get_departments():
    departments = Department.query.order_by(Department.name.asc()).all()
    return {"departments": [serialize_department(department) for department in departments]}, 200


def get_doctors_by_specialization(specialization: str):
    if not specialization:
        return {"message": "specialization query parameter is required"}, 400

    doctors = (
        Doctor.query.filter_by(is_active=True, is_blacklisted=False)
        .filter(Doctor.specialization.ilike(f"%{specialization}%"))
        .order_by(Doctor.name.asc())
        .all()
    )

    return {"doctors": [serialize_doctor(doctor) for doctor in doctors]}, 200


def get_doctor_availability(doctor_id: int):
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True, is_blacklisted=False).first()
    if not doctor:
        return {"message": "Doctor not found or unavailable"}, 404

    availabilities = (
        DoctorAvailability.query.filter_by(doctor_id=doctor.id)
        .order_by(DoctorAvailability.date.asc())
        .all()
    )

    return {
        "doctor": serialize_doctor(doctor),
        "availabilities": [
            {
                "id": availability.id,
                "date": availability.date.isoformat(),
                "available_slots": availability.available_slots,
            }
            for availability in availabilities
        ],
    }, 200


def book_appointment(user_id: int, payload: dict):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return {"message": "Patient profile not found"}, 404

    required_fields = ["doctor_id", "appointment_date", "appointment_time"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return {"message": f"Missing fields: {', '.join(missing)}"}, 400

    doctor = Doctor.query.filter_by(
        id=payload["doctor_id"], is_active=True, is_blacklisted=False
    ).first()
    if not doctor:
        return {"message": "Doctor not found or unavailable"}, 404

    parsed_date, parsed_time, error = parse_slot(payload["appointment_date"], payload["appointment_time"])
    if error:
        return {"message": error}, 400

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=parsed_date,
        appointment_time=parsed_time,
        status=AppointmentStatus.BOOKED.value,
    )

    db.session.add(appointment)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Selected slot is already booked for this doctor"}, 409

    return {
        "message": "Appointment booked successfully",
        "appointment": serialize_appointment(appointment),
    }, 201


def reschedule_appointment(user_id: int, appointment_id: int, payload: dict):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return {"message": "Patient profile not found"}, 404

    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=patient.id).first()
    if not appointment:
        return {"message": "Appointment not found"}, 404

    if appointment.status == AppointmentStatus.CANCELLED.value:
        return {"message": "Cancelled appointment cannot be rescheduled"}, 400

    required_fields = ["appointment_date", "appointment_time"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return {"message": f"Missing fields: {', '.join(missing)}"}, 400

    parsed_date, parsed_time, error = parse_slot(payload["appointment_date"], payload["appointment_time"])
    if error:
        return {"message": error}, 400

    appointment.appointment_date = parsed_date
    appointment.appointment_time = parsed_time

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Selected slot is already booked for this doctor"}, 409

    return {
        "message": "Appointment rescheduled successfully",
        "appointment": serialize_appointment(appointment),
    }, 200


def cancel_patient_appointment(user_id: int, appointment_id: int):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return {"message": "Patient profile not found"}, 404

    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=patient.id).first()
    if not appointment:
        return {"message": "Appointment not found"}, 404

    appointment.status = AppointmentStatus.CANCELLED.value
    db.session.commit()

    return {
        "message": "Appointment cancelled successfully",
        "appointment": serialize_appointment(appointment),
    }, 200


def get_treatment_history(user_id: int):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return {"message": "Patient profile not found"}, 404

    treatments = (
        Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(Appointment.patient_id == patient.id)
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        .all()
    )

    return {
        "treatments": [
            {
                "id": treatment.id,
                "appointment_id": treatment.appointment_id,
                "doctor_id": treatment.appointment.doctor_id,
                "doctor_name": treatment.appointment.doctor.name,
                "diagnosis": treatment.diagnosis,
                "prescription": treatment.prescription,
                "notes": treatment.notes,
                "appointment_date": treatment.appointment.appointment_date.isoformat(),
                "appointment_time": treatment.appointment.appointment_time.isoformat(),
            }
            for treatment in treatments
        ]
    }, 200


def parse_slot(raw_date: str, raw_time: str):
    try:
        parsed_date = date.fromisoformat(raw_date)
    except ValueError:
        return None, None, "Invalid appointment_date format. Use YYYY-MM-DD"

    try:
        parsed_time = datetime.strptime(raw_time, "%H:%M").time()
    except ValueError:
        return None, None, "Invalid appointment_time format. Use HH:MM"

    return parsed_date, parsed_time, None


def serialize_department(department: Department):
    return {
        "id": department.id,
        "name": department.name,
        "description": department.description,
    }


def serialize_doctor(doctor: Doctor):
    return {
        "id": doctor.id,
        "name": doctor.name,
        "specialization": doctor.specialization,
        "department_id": doctor.department_id,
        "department_name": doctor.department.name if doctor.department else None,
        "availability_info": doctor.availability_info,
    }


def serialize_appointment(appointment: Appointment):
    return {
        "id": appointment.id,
        "doctor_id": appointment.doctor_id,
        "doctor_name": appointment.doctor.name,
        "appointment_date": appointment.appointment_date.isoformat(),
        "appointment_time": appointment.appointment_time.isoformat(),
        "status": appointment.status,
        "created_at": appointment.created_at.isoformat(),
    }
