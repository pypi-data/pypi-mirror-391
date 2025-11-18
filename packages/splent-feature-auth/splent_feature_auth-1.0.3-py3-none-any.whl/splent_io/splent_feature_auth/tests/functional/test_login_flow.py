from flask import url_for
import pytest


@pytest.fixture(scope="function")
def auth_test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client

def test_login_success(auth_test_client, auth_test_user):
    response = auth_test_client.post("/login", data=dict(
        email="user1@example.com", password="1234"
    ), follow_redirects=True)

    assert b"Invalid credentials" not in response.data


def test_login_unsuccessful_bad_email(auth_test_client):
    response = auth_test_client.post(
        "/login",
        data=dict(email="bademail@example.com", password="test1234"),
        follow_redirects=True,
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"
    auth_test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_password(auth_test_client):
    response = auth_test_client.post(
        "/login",
        data=dict(email="user1@example.com", password="wrongpass"),
        follow_redirects=True,
    )

    assert b"Invalid credentials" in response.data
