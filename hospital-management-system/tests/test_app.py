from datetime import date, time, timedelta

import pytest
from flask_jwt_extended import create_access_token

from backend.app import create_app
from backend.extensions import db
from backend.models.appointment import Appointment, AppointmentStatus
from backend.models.department import Department
from backend.models.doctor import Doctor
from backend.models.patient import Patient
from backend.models.treatment import Treatment
from backend.models.user import Role, User
from backend.tasks.tasks import generate_patient_treatment_csv


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = "redis://localhost:6379/0"
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    ADMIN_DEFAULT_USERNAME = "admin"
    ADMIN_DEFAULT_EMAIL = "admin@test.local"
    ADMIN_DEFAULT_PASSWORD = "Admin@123"


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def seed_patient_context(app):
    with app.app_context():
        department = Department(name="Cardiology", description="Heart care")

        doctor_user = User(username="drsmith", role=Role.DOCTOR.value)
        doctor_user.set_password("secret")
        doctor = Doctor(
            user=doctor_user,
            name="Dr. Smith",
            specialization="Cardiology",
            department=department,
            is_active=True,
            is_blacklisted=False,
        )

        patient_user = User(username="john", role=Role.PATIENT.value)
        patient_user.set_password("secret")
        patient = Patient(user=patient_user, name="John Doe", email="john@example.com")

        db.session.add_all([department, doctor_user, doctor, patient_user, patient])
        db.session.commit()

        token = create_access_token(identity=str(patient_user.id), additional_claims={"role": "patient"})

        return {
            "token": token,
            "doctor_id": doctor.id,
            "patient_id": patient.id,
        }


def seed_doctor_context(app):
    with app.app_context():
        department = Department(name="Neurology", description="Brain care")

        doctor_user = User(username="drhouse", role=Role.DOCTOR.value)
        doctor_user.set_password("secret")
        doctor = Doctor(
            user=doctor_user,
            name="Dr. House",
            specialization="Neurology",
            department=department,
            is_active=True,
            is_blacklisted=False,
        )

        patient_user = User(username="jane", role=Role.PATIENT.value)
        patient_user.set_password("secret")
        patient = Patient(user=patient_user, name="Jane Roe", email="jane@example.com")

        db.session.add_all([department, doctor_user, doctor, patient_user, patient])
        db.session.commit()

        token = create_access_token(identity=str(doctor_user.id), additional_claims={"role": "doctor"})

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(hour=10, minute=0),
            status=AppointmentStatus.BOOKED.value,
        )
        db.session.add(appointment)
        db.session.commit()

        return {"token": token, "appointment_id": appointment.id}


def test_health_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200


def test_patient_can_book_and_prevent_double_booking(client, app):
    context = seed_patient_context(app)
    headers = {"Authorization": f"Bearer {context['token']}"}

    payload = {
        "doctor_id": context["doctor_id"],
        "appointment_date": (date.today() + timedelta(days=1)).isoformat(),
        "appointment_time": "10:30",
    }

    first = client.post("/patient/appointments", json=payload, headers=headers)
    assert first.status_code == 201

    second = client.post("/patient/appointments", json=payload, headers=headers)
    assert second.status_code == 409
    assert "already booked" in second.get_json()["message"]


def test_patient_dashboard_search_and_treatments(client, app):
    context = seed_patient_context(app)
    headers = {"Authorization": f"Bearer {context['token']}"}

    with app.app_context():
        appointment = Appointment(
            patient_id=context["patient_id"],
            doctor_id=context["doctor_id"],
            appointment_date=date.today() - timedelta(days=2),
            appointment_time=time(hour=9, minute=0),
            status=AppointmentStatus.COMPLETED.value,
        )
        db.session.add(appointment)
        db.session.flush()

        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis="Migraine",
            prescription="Painkiller",
            notes="Hydration advised",
        )
        db.session.add(treatment)
        db.session.commit()

    dashboard = client.get("/patient/dashboard", headers=headers)
    assert dashboard.status_code == 200
    dashboard_json = dashboard.get_json()
    assert len(dashboard_json["available_departments"]) == 1
    assert len(dashboard_json["available_doctors"]) == 1
    assert len(dashboard_json["appointment_history"]) == 1

    search = client.get("/patient/search?doctor_name=smith", headers=headers)
    assert search.status_code == 200
    assert len(search.get_json()["doctors"]) == 1

    treatments = client.get("/patient/treatments", headers=headers)
    assert treatments.status_code == 200
    treatment_json = treatments.get_json()["treatments"]
    assert len(treatment_json) == 1
    assert treatment_json[0]["diagnosis"] == "Migraine"


def test_cached_patient_lookup_routes(client, app):
    context = seed_patient_context(app)
    headers = {"Authorization": f"Bearer {context['token']}"}

    with app.app_context():
        from backend.models.doctor_availability import DoctorAvailability

        availability = DoctorAvailability(
            doctor_id=context["doctor_id"],
            date=date.today() + timedelta(days=1),
            available_slots="09:00-11:00",
        )
        db.session.add(availability)
        db.session.commit()

    departments = client.get("/patient/departments", headers=headers)
    assert departments.status_code == 200
    assert len(departments.get_json()["departments"]) == 1

    doctors = client.get("/patient/doctors/by-specialization?specialization=cardio", headers=headers)
    assert doctors.status_code == 200
    assert len(doctors.get_json()["doctors"]) == 1

    availability = client.get(f"/patient/doctors/{context['doctor_id']}/availability", headers=headers)
    assert availability.status_code == 200
    assert len(availability.get_json()["availabilities"]) == 1


def test_generate_treatment_csv_task(client, app):
    context = seed_patient_context(app)

    with app.app_context():
        appointment = Appointment(
            patient_id=context["patient_id"],
            doctor_id=context["doctor_id"],
            appointment_date=date.today(),
            appointment_time=time(hour=11, minute=0),
            status=AppointmentStatus.COMPLETED.value,
        )
        db.session.add(appointment)
        db.session.flush()

        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis="Flu",
            prescription="Rest",
            notes="Drink warm fluids",
        )
        db.session.add(treatment)
        db.session.commit()

        result = generate_patient_treatment_csv(context["patient_id"])

    assert result["status"] == "completed"
    assert result["records"] == 1


def test_booking_validation_rejects_invalid_payload(client, app):
    context = seed_patient_context(app)
    headers = {"Authorization": f"Bearer {context['token']}"}

    response = client.post(
        "/patient/appointments",
        json={"doctor_id": "abc", "appointment_date": "bad", "appointment_time": "10:00"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "doctor_id" in response.get_json()["message"]


def test_doctor_status_transition_enforced(client, app):
    context = seed_doctor_context(app)
    headers = {"Authorization": f"Bearer {context['token']}"}

    invalid_cancel = client.post(f"/doctor/appointment/{context['appointment_id']}/cancel", headers=headers)
    assert invalid_cancel.status_code == 400
    assert "Invalid status transition" in invalid_cancel.get_json()["message"]

    completed = client.post(f"/doctor/appointment/{context['appointment_id']}/complete", headers=headers)
    assert completed.status_code == 200

    cancelled = client.post(f"/doctor/appointment/{context['appointment_id']}/cancel", headers=headers)
    assert cancelled.status_code == 200
