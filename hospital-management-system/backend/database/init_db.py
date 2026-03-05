from backend.services.user_service import create_default_admin


def initialize_database(db, config):
    db.create_all()
    create_default_admin(config, db)
