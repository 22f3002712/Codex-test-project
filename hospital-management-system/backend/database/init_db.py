"""Database initialization utilities for creating SQLite schema programmatically."""

from backend.models import (  # noqa: F401
    Appointment,
    Department,
    Doctor,
    DoctorAvailability,
    Patient,
    Treatment,
    User,
)
from backend.services.user_service import create_default_admin


def initialize_database(db, config):
    """Create all database tables and seed required baseline data."""
    db.create_all()
    create_default_admin(config, db)


def reset_database(db, config):
    """Drop and recreate all tables for local development/testing."""
    db.drop_all()
    initialize_database(db, config)
