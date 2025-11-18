from splent_framework.fixtures.fixtures import *
import pytest
from splent_io.splent_feature_auth.models import User
from splent_framework.db import db


@pytest.fixture(scope="function")
def auth_test_user(test_app):
    with test_app.app_context():
        user = User(email="user1@example.com", active=True)
        user.set_password("1234")
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture(scope="function")
def logged_in_client(test_client, auth_test_user):
    test_client.post("/login", data={
        "email": "user1@example.com",
        "password": "1234"
    }, follow_redirects=True)
    return test_client

@pytest.fixture(scope="function")
def inactive_user(test_app):
    with test_app.app_context():
        user = User(email="inactive@example.com", active=False)
        user.set_password("1234")
        db.session.add(user)
        db.session.commit()
        return user
