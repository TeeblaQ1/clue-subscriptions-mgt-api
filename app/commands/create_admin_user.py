import click
from flask import current_app
from app.models.users import User
from app.extensions import db

@click.command("create-admin")
@click.argument("email")
@click.argument("password")
def create_admin(email, password):
    """Used to create an admin user with the specified email and password."""
    with current_app.app_context():
        if db.session.query(User).filter_by(email=email).first():
            click.echo(f"User with email {email} already exists.", color="red")
            return
    
        user = User(email=email)
        user.set_password(password)
        user.is_admin = True
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin user {email} created successfully.", color="green")
