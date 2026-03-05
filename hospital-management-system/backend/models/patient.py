from backend.extensions import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    is_blacklisted = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship("User", back_populates="patient_profile")
    appointments = db.relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan", lazy=True
    )
