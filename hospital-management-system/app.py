"""Project entrypoint so the app can be started with `python app.py`."""

from backend.app import app


if __name__ == "__main__":
    # Use Flask's built-in server for local development submissions.
    app.run(debug=True)
