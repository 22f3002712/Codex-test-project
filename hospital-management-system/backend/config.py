import os

from celery.schedules import crontab


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///hospital_management.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "UTC")
    PATIENT_REMINDER_WEBHOOK_URL = os.getenv("PATIENT_REMINDER_WEBHOOK_URL")
    CSV_EXPORT_DIR = os.getenv("CSV_EXPORT_DIR", "exports")

    CELERY_BEAT_SCHEDULE = {
        "daily-appointment-reminders": {
            "task": "tasks.daily_reminder_job",
            "schedule": crontab(minute=0, hour=7),
        },
        "monthly-doctor-report": {
            "task": "tasks.monthly_doctor_report_job",
            "schedule": crontab(minute=0, hour=8, day_of_month="1"),
        },
    }

    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", REDIS_URL)
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

    ADMIN_DEFAULT_USERNAME = os.getenv("ADMIN_DEFAULT_USERNAME", "admin")
    ADMIN_DEFAULT_EMAIL = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@hms.local")
    ADMIN_DEFAULT_PASSWORD = os.getenv("ADMIN_DEFAULT_PASSWORD", "Admin@123")
