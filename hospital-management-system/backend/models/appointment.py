from datetime import date, datetime, time
from enum import Enum

from backend.extensions import db


class AppointmentStatus(Enum):
    BOOKED = "Booked"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Appointment(db.Model):
    __tablename__ = "appointments"
    __table_args__ = (
        db.UniqueConstraint(
            "doctor_id",
            "appointment_date",
            "appointment_time",
            name="uq_doctor_appointment_slot",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False, default=date.today)
    appointment_time = db.Column(db.Time, nullable=False, default=time(hour=9, minute=0))
    status = db.Column(db.String(20), nullable=False, default=AppointmentStatus.BOOKED.value)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    treatments = db.relationship(
        "Treatment", back_populates="appointment", cascade="all, delete-orphan", lazy=True
    )
