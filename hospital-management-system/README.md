# Hospital Management System (HMS)

Initial full-stack architecture for a local Hospital Management System using:

- **Backend:** Flask
- **Frontend:** VueJS
- **Styling:** Bootstrap
- **Template engine:** Jinja2 (backend entry page only)
- **Database:** SQLite (via SQLAlchemy models)
- **Cache / Broker / Result backend:** Redis
- **Background jobs:** Celery with Redis

## Project Structure

```text
hospital-management-system/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── tasks/
│   ├── cache/
│   ├── database/
│   └── templates/
├── frontend/
│   ├── index.html
│   ├── js/
│   ├── components/
│   └── views/
├── tests/
├── docker/
├── requirements.txt
└── README.md
```

## Quick Start (Local)

1. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start Redis (required for cache/celery)**
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```
4. **Run Flask app**
   ```bash
   cd backend
   flask --app app run
   ```
5. **Open frontend**
   - Open `frontend/index.html` directly in browser, or serve it via:
   ```bash
   python -m http.server 8080 --directory frontend
   ```

## Database Initialization Rules

- SQLite database is created automatically from SQLAlchemy models at app startup.
- Default Admin user is auto-created on first run.
- No manual schema creation is required.

Default admin credentials (override via environment variables):

- Username: `admin`
- Email: `admin@hms.local`
- Password: `Admin@123`

## Role-Based Access Control

The backend includes JWT authentication and role-protected endpoints:

- `GET /api/dashboard/admin` (Admin only)
- `GET /api/dashboard/doctor` (Doctor only)
- `GET /api/dashboard/patient` (Patient only)

## Celery Worker

Run a worker from the project root:

```bash
celery -A backend.extensions.celery worker --loglevel=info
```
