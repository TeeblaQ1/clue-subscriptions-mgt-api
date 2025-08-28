from flask import Flask
from app.config import Config
from app.commands.create_admin_user import create_admin
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .routes.subscriptions import bp as subscriptions_bp
    app.register_blueprint(subscriptions_bp)

    app.cli.add_command(create_admin)
    return app
