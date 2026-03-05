from flask_jwt_extended import create_access_token

from backend.extensions import db
from backend.models.patient import Patient
from backend.models.user import Role, User


def login_user(username: str, password: str):
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return None

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return {"access_token": token, "role": user.role}


def register_patient(payload: dict):
    username = payload.get("username")
    email = payload.get("email")
    password = payload.get("password")
    name = payload.get("name")

    if payload.get("role") and payload.get("role") != Role.PATIENT.value:
        return {"message": "Only patient registration is allowed"}, 403

    required_fields = ["username", "email", "password", "name"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return {"message": f"Missing fields: {', '.join(missing)}"}, 400

    if User.query.filter_by(username=username).first():
        return {"message": "Username already exists"}, 409

    if Patient.query.filter_by(email=email).first():
        return {"message": "Patient email already exists"}, 409

    user = User(username=username, role=Role.PATIENT.value)
    user.set_password(password)

    patient = Patient(
        user=user,
        name=name,
        email=email,
        phone=payload.get("phone"),
        address=payload.get("address"),
        date_of_birth=payload.get("date_of_birth"),
    )

    db.session.add_all([user, patient])
    db.session.commit()

    return {"message": "Patient registered successfully"}, 201
