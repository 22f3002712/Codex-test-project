import csv
import json
import logging
from collections import Counter
from datetime import date
from pathlib import Path
from urllib import error, request

from backend.extensions import celery
from backend.models.appointment import Appointment, AppointmentStatus
from backend.models.doctor import Doctor
from backend.models.patient import Patient
from backend.models.treatment import Treatment

logger = logging.getLogger(__name__)


@celery.task(name="tasks.daily_reminder_job")
def daily_reminder_job():
    today = date.today()
    appointments = (
        Appointment.query.filter_by(appointment_date=today, status=AppointmentStatus.BOOKED.value)
        .order_by(Appointment.appointment_time.asc())
        .all()
    )

    reminders_sent = 0
    for appointment in appointments:
        if send_reminder(appointment):
            reminders_sent += 1

    return {
        "date": today.isoformat(),
        "appointments_checked": len(appointments),
        "reminders_sent": reminders_sent,
    }


@celery.task(name="tasks.monthly_doctor_report_job")
def monthly_doctor_report_job():
    doctors = Doctor.query.filter_by(is_active=True).all()
    reports_sent = 0

    for doctor in doctors:
        report = build_doctor_report(doctor.id)
        if send_doctor_report_email(doctor, report):
            reports_sent += 1

    return {
        "doctors_checked": len(doctors),
        "reports_sent": reports_sent,
    }


@celery.task(name="tasks.generate_patient_treatment_csv")
def generate_patient_treatment_csv(patient_id: int):
    patient = Patient.query.get(patient_id)
    if not patient:
        return {"status": "error", "message": "Patient not found"}

    treatments = (
        Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(Appointment.patient_id == patient_id)
        .order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc())
        .all()
    )

    export_dir = Path(celery.conf.get("CSV_EXPORT_DIR", "exports"))
    export_dir.mkdir(parents=True, exist_ok=True)
    file_path = export_dir / f"treatment_history_patient_{patient_id}.csv"

    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "patient_id",
                "doctor_name",
                "appointment_date",
                "diagnosis",
                "prescription",
                "notes",
            ],
        )
        writer.writeheader()

        for treatment in treatments:
            writer.writerow(
                {
                    "patient_id": patient_id,
                    "doctor_name": treatment.appointment.doctor.name,
                    "appointment_date": treatment.appointment.appointment_date.isoformat(),
                    "diagnosis": treatment.diagnosis,
                    "prescription": treatment.prescription or "",
                    "notes": treatment.notes or "",
                }
            )

    return {
        "status": "completed",
        "patient_id": patient_id,
        "records": len(treatments),
        "file_path": str(file_path),
    }


def send_reminder(appointment: Appointment) -> bool:
    payload = {
        "patient_id": appointment.patient_id,
        "patient_email": appointment.patient.email,
        "doctor_name": appointment.doctor.name,
        "appointment_date": appointment.appointment_date.isoformat(),
        "appointment_time": appointment.appointment_time.isoformat(),
    }

    webhook_url = celery.conf.get("PATIENT_REMINDER_WEBHOOK_URL")
    if webhook_url:
        return post_webhook(webhook_url, payload)

    logger.info("Sending email reminder payload: %s", payload)
    return True


def build_doctor_report(doctor_id: int):
    completed_appointments = (
        Appointment.query.filter_by(doctor_id=doctor_id, status=AppointmentStatus.COMPLETED.value)
        .order_by(Appointment.appointment_date.asc())
        .all()
    )

    treatments = (
        Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.COMPLETED.value,
        )
        .all()
    )

    diagnosis_summary = Counter(treatment.diagnosis for treatment in treatments)
    prescriptions_summary = Counter(treatment.prescription for treatment in treatments if treatment.prescription)

    return {
        "appointments_completed": len(completed_appointments),
        "diagnosis_summary": dict(diagnosis_summary),
        "treatments_given": dict(prescriptions_summary),
    }


def send_doctor_report_email(doctor: Doctor, report: dict) -> bool:
    if not doctor.user:
        return False

    logger.info(
        "Sending monthly report to doctor %s (%s): %s",
        doctor.name,
        doctor.user.username,
        report,
    )
    return True


def post_webhook(url: str, payload: dict) -> bool:
    request_data = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url,
        data=request_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=10):
            return True
    except error.URLError:
        logger.exception("Failed to deliver webhook reminder")
        return False
