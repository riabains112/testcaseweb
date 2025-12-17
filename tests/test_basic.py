import os
import sys

# Make sure the project root (where 'app' lives) is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    """Create a fresh app + in-memory database for each test."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.drop_all()
        db.create_all()

        # create a test admin user
        admin = User(
            name="Test Admin",
            email="admin@example.com",
            role="admin",
        )
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    yield app

    # teardown
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client for making requests."""
    return app.test_client()


def test_home_requires_login(client):
    """Unauthenticated users should be redirected to login page."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_can_login(client):
    """Valid credentials should log the admin in and show the dashboard."""
    response = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome" in response.data
    assert b"Test Admin" in response.data
