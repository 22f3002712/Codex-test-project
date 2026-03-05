from backend.extensions import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship("User", back_populates="doctor_profile")
    department = db.relationship("Department", back_populates="doctors")
    availabilities = db.relationship("DoctorAvailability", back_populates="doctor", lazy=True)
    appointments = db.relationship("Appointment", back_populates="doctor", lazy=True)
