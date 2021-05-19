from application import app, db
from application.core.models import AdminUser


@app.cli.command()
def createsuperuser():
    """Create superuser for administration panel"""
    email = input("Type user email: ")
    password = input("Type password: ")
    user_admin = AdminUser(email=email)
    user_admin.set_password(password)
    db.session.add(user_admin)
    db.session.commit()
    print("Superuser {} created!".format(email))
