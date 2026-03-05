from enum import Enum

from werkzeug.security import check_password_hash, generate_password_hash

from backend.extensions import db


class Role(Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    doctor_profile = db.relationship("Doctor", back_populates="user", uselist=False)
    patient_profile = db.relationship("Patient", back_populates="user", uselist=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
