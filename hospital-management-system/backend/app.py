import logging

from flask import Flask, jsonify, render_template
from werkzeug.exceptions import HTTPException

from backend.config import Config
from backend.database.init_db import initialize_database
from backend.extensions import cache, db, init_celery, jwt
from backend.routes import admin_bp, auth_bp, dashboard_bp, doctor_bp, patient_bp


def configure_logging(app: Flask):
    logging.basicConfig(
        level=app.config.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    configure_logging(app)

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    init_celery(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": f"Invalid token: {error}"}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"message": f"Authorization required: {error}"}), 401

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({"message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        app.logger.exception("Unhandled API error")
        return jsonify({"message": "Internal server error"}), 500

    @app.get("/")
    def index():
        return render_template("index.html")

    with app.app_context():
        initialize_database(db, app.config)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
