# Hospital Management System

Hospital Management System built with a **Flask API backend** and **VueJS frontend**.

## Stack

- Flask
- VueJS
- Bootstrap
- SQLite
- Redis
- Celery

## Project Layout

```text
hospital-management-system/
├── app.py                      # Local run entrypoint: python app.py
├── backend/
│   ├── app.py                  # Flask app factory and API setup
│   ├── celery_worker.py        # Celery app bootstrap
│   ├── database/
│   │   ├── init_db.py          # Programmatic schema creation
│   │   └── seed_data.py        # Seed utility functions
├── frontend/
├── sample_data/
│   └── seed_data.json          # Sample records used by seed script
├── scripts/
│   └── seed_database.py        # CLI seed script
└── requirements.txt
```

## Local Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Seed database with sample data (optional but recommended):

```bash
python scripts/seed_database.py
```

## Run the Project Locally

Start each service in a separate terminal from the project root.

1. Flask API and backend-rendered root page:

```bash
python app.py
```

2. Redis server:

```bash
redis-server
```

3. Celery worker:

```bash
celery -A backend.celery_worker.celery_app worker --loglevel=info
```

> Note: Celery worker requires Redis to be running.

## Database Notes

- The SQLite schema is created programmatically via SQLAlchemy (`db.create_all()`).
- On app start, the app creates schema and default admin user if they do not exist.
- Seed data is idempotent by unique keys (re-running the seed script does not duplicate records).

## Default Admin

- Username: `admin`
- Password: `Admin@123`

## Tests

Run the test suite with:

```bash
pytest
```
