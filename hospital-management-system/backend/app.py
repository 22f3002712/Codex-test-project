from flask import Flask, render_template

from backend.config import Config
from backend.database.init_db import initialize_database
from backend.extensions import db, init_celery, jwt
from backend.routes import admin_bp, auth_bp, dashboard_bp, doctor_bp



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    init_celery(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)

    @app.get("/")
    def index():
        return render_template("index.html")

    with app.app_context():
        initialize_database(db, app.config)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
