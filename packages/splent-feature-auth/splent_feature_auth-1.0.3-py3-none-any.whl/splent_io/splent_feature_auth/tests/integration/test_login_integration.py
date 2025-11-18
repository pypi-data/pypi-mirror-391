def test_login_sets_session_cookie(test_client, auth_test_user):
    response = test_client.post("/login", data={
        "email": "user1@example.com",
        "password": "1234"
    }, follow_redirects=True)

    assert b"Edit profile" in response.data