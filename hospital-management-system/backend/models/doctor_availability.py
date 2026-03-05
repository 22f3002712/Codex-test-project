from datetime import date

from backend.extensions import db


class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availabilities"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    available_slots = db.Column(db.Text, nullable=False)

    doctor = db.relationship("Doctor", back_populates="availabilities")
