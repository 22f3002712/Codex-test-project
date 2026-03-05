from backend.models.user import Role, User


def create_default_admin(config, db):
    existing_admin = User.query.filter_by(role=Role.ADMIN.value).first()
    if existing_admin:
        return existing_admin

    admin = User(
        username=config["ADMIN_DEFAULT_USERNAME"],
        email=config["ADMIN_DEFAULT_EMAIL"],
        role=Role.ADMIN.value,
    )
    admin.set_password(config["ADMIN_DEFAULT_PASSWORD"])
    db.session.add(admin)
    db.session.commit()
    return admin
