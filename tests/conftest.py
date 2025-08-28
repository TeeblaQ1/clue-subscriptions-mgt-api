import os
import pytest
from app import create_app, db
from app.models import SubscriptionPlan, User

@pytest.fixture(scope="function")
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"],
    })

    with app.app_context():
        db.create_all()

        p1 = SubscriptionPlan(name="Basic", description="Basic plan", price_cents=1000)
        p2 = SubscriptionPlan(name="Pro", description="Pro plan", price_cents=2000)
        admin = User(email="admin@test.com", is_admin=True)
        admin.set_password("password")

        db.session.add_all([p1, p2, admin])
        db.session.commit()

        yield app

        # teardown
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()
