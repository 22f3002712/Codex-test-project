from backend.extensions import db
from backend.models.appointment import Appointment
from backend.models.department import Department
from backend.models.doctor import Doctor
from backend.models.patient import Patient
from backend.models.user import Role, User


def get_dashboard_metrics():
    return {
        "total_doctors": Doctor.query.count(),
        "total_patients": Patient.query.count(),
        "total_appointments": Appointment.query.count(),
    }, 200


def create_doctor(payload: dict):
    required_fields = ["username", "password", "name", "specialization", "department_id"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return {"message": f"Missing fields: {', '.join(missing)}"}, 400

    username = payload["username"]
    if User.query.filter_by(username=username).first():
        return {"message": "Username already exists"}, 409

    department = Department.query.get(payload["department_id"])
    if not department:
        return {"message": "Department not found"}, 404

    user = User(username=username, role=Role.DOCTOR.value)
    user.set_password(payload["password"])

    doctor = Doctor(
        user=user,
        name=payload["name"],
        specialization=payload["specialization"],
        department_id=department.id,
        availability_info=payload.get("availability_info"),
        is_active=payload.get("is_active", True),
        is_blacklisted=payload.get("is_blacklisted", False),
    )

    db.session.add_all([user, doctor])
    db.session.commit()

    return serialize_doctor(doctor), 201


def update_doctor(doctor_id: int, payload: dict):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return {"message": "Doctor not found"}, 404

    if "name" in payload:
        doctor.name = payload["name"]
    if "specialization" in payload:
        doctor.specialization = payload["specialization"]
    if "availability_info" in payload:
        doctor.availability_info = payload["availability_info"]
    if "is_active" in payload:
        doctor.is_active = bool(payload["is_active"])
    if "is_blacklisted" in payload:
        doctor.is_blacklisted = bool(payload["is_blacklisted"])

    if "department_id" in payload:
        department = Department.query.get(payload["department_id"])
        if not department:
            return {"message": "Department not found"}, 404
        doctor.department_id = department.id

    db.session.commit()
    return serialize_doctor(doctor), 200


def delete_doctor(doctor_id: int):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return {"message": "Doctor not found"}, 404

    user = doctor.user
    db.session.delete(doctor)
    if user:
        db.session.delete(user)
    db.session.commit()
    return {"message": "Doctor deleted successfully"}, 200


def blacklist_doctor(doctor_id: int):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return {"message": "Doctor not found"}, 404

    doctor.is_blacklisted = True
    doctor.is_active = False
    db.session.commit()
    return {"message": "Doctor blacklisted successfully", "doctor": serialize_doctor(doctor)}, 200


def blacklist_patient(patient_id: int):
    patient = Patient.query.get(patient_id)
    if not patient:
        return {"message": "Patient not found"}, 404

    patient.is_blacklisted = True
    db.session.commit()
    return {"message": "Patient blacklisted successfully", "patient": serialize_patient(patient)}, 200


def search_records(doctor_name=None, specialization=None, patient_name=None):
    if doctor_name:
        doctors = Doctor.query.filter(Doctor.name.ilike(f"%{doctor_name}%")).all()
        return {"doctors": [serialize_doctor(doctor) for doctor in doctors]}, 200

    if specialization:
        doctors = Doctor.query.filter(Doctor.specialization.ilike(f"%{specialization}%")).all()
        return {"doctors": [serialize_doctor(doctor) for doctor in doctors]}, 200

    if patient_name:
        patients = Patient.query.filter(Patient.name.ilike(f"%{patient_name}%")).all()
        return {"patients": [serialize_patient(patient) for patient in patients]}, 200

    return {
        "message": "Provide one query parameter: doctor_name, specialization, or patient_name"
    }, 400


def get_all_appointments():
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return {
        "appointments": [
            {
                "id": appointment.id,
                "doctor_id": appointment.doctor_id,
                "doctor_name": appointment.doctor.name,
                "patient_id": appointment.patient_id,
                "patient_name": appointment.patient.name,
                "appointment_date": appointment.appointment_date.isoformat(),
                "appointment_time": appointment.appointment_time.isoformat(),
                "status": appointment.status,
                "created_at": appointment.created_at.isoformat(),
            }
            for appointment in appointments
        ]
    }, 200


def serialize_doctor(doctor: Doctor):
    return {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "name": doctor.name,
        "specialization": doctor.specialization,
        "department_id": doctor.department_id,
        "availability_info": doctor.availability_info,
        "is_active": doctor.is_active,
        "is_blacklisted": doctor.is_blacklisted,
    }


def serialize_patient(patient: Patient):
    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "name": patient.name,
        "email": patient.email,
        "phone": patient.phone,
        "is_blacklisted": patient.is_blacklisted,
    }
