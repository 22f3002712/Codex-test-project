from datetime import datetime

from backend.extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="scheduled")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    treatments = db.relationship("Treatment", back_populates="appointment", lazy=True)
