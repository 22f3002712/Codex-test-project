from backend.app import create_app
from backend.extensions import celery, init_celery

flask_app = create_app()
celery_app = init_celery(flask_app)

# Ensure task modules are imported when worker starts.
from backend.tasks import tasks as _tasks  # noqa: F401,E402
