from datetime import date, datetime

from backend.models.appointment import AppointmentStatus

VALID_STATUS_TRANSITIONS = {
    AppointmentStatus.BOOKED.value: {AppointmentStatus.COMPLETED.value},
    AppointmentStatus.COMPLETED.value: {AppointmentStatus.CANCELLED.value},
    AppointmentStatus.CANCELLED.value: set(),
}


def validate_booking_payload(payload: dict):
    required_fields = ["doctor_id", "appointment_date", "appointment_time"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return None, f"Missing fields: {', '.join(missing)}"

    try:
        doctor_id = int(payload["doctor_id"])
    except (TypeError, ValueError):
        return None, "doctor_id must be a valid integer"

    if doctor_id <= 0:
        return None, "doctor_id must be greater than zero"

    parsed_date, parsed_time, error = parse_slot(payload["appointment_date"], payload["appointment_time"])
    if error:
        return None, error

    if parsed_date < date.today():
        return None, "appointment_date cannot be in the past"

    return {
        "doctor_id": doctor_id,
        "appointment_date": parsed_date,
        "appointment_time": parsed_time,
    }, None


def parse_slot(raw_date: str, raw_time: str):
    try:
        parsed_date = date.fromisoformat(raw_date)
    except (TypeError, ValueError):
        return None, None, "Invalid appointment_date format. Use YYYY-MM-DD"

    try:
        parsed_time = datetime.strptime(raw_time, "%H:%M").time()
    except (TypeError, ValueError):
        return None, None, "Invalid appointment_time format. Use HH:MM"

    return parsed_date, parsed_time, None


def validate_status_transition(current_status: str, requested_status: str):
    allowed_transitions = VALID_STATUS_TRANSITIONS.get(current_status, set())
    if requested_status not in allowed_transitions:
        return (
            False,
            f"Invalid status transition from {current_status} to {requested_status}. "
            "Allowed sequence: Booked -> Completed -> Cancelled",
        )
    return True, None
