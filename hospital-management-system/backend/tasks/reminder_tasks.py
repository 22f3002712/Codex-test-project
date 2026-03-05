from backend.extensions import celery


@celery.task(name="tasks.send_appointment_reminder")
def send_appointment_reminder(appointment_id):
    return {"status": "queued", "appointment_id": appointment_id}
