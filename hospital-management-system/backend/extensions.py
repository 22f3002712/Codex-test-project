from celery import Celery
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
celery = Celery(__name__)


def init_celery(app):
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_ignore_result=False,
        timezone=app.config["CELERY_TIMEZONE"],
        beat_schedule=app.config["CELERY_BEAT_SCHEDULE"],
        imports=("backend.tasks.tasks",),
        PATIENT_REMINDER_WEBHOOK_URL=app.config.get("PATIENT_REMINDER_WEBHOOK_URL"),
        CSV_EXPORT_DIR=app.config.get("CSV_EXPORT_DIR", "exports"),
    )

    class FlaskTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskTask
    return celery
