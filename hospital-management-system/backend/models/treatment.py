from datetime import datetime

from backend.extensions import db


class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(
        db.Integer, db.ForeignKey("appointments.id"), nullable=False
    )
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    appointment = db.relationship("Appointment", back_populates="treatments")
