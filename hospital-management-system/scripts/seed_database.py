"""CLI helper for seeding local SQLite with sample data."""

from backend.app import create_app
from backend.database.seed_data import seed_database
from backend.extensions import db


def main() -> None:
    """Create schema if needed, then load deterministic sample records."""
    app = create_app()
    with app.app_context():
        db.create_all()
        summary = seed_database(db)

    print("Seed completed:")
    for model_name, count in summary.items():
        print(f"- {model_name}: {count}")


if __name__ == "__main__":
    main()
