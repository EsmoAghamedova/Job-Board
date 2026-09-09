from app.models import User
from tests.conftest import login, register


def test_registration_and_login(client):
    response = register(client, "Ava Applicant", "ava@example.com")
    assert response.status_code == 200
    response = login(client, "ava@example.com")
    assert response.status_code == 200
    assert b"Logout" in response.data


def test_invalid_login_is_rejected(client):
    register(client, "Ava Applicant", "ava@example.com")
    response = login(client, "ava@example.com", "wrong-password")
    assert b"Invalid email or password" in response.data


def test_login_returns_to_safe_requested_page(client):
    register(client, "Ava Applicant", "ava@example.com")
    response = client.post(
        "/auth/login?next=/jobs/1/apply",
        data={"email": "ava@example.com", "password": "LongPassword123!"},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/jobs/1/apply")


def test_registration_rejects_easy_and_medium_one_passwords(client):
    for password in ("abc123", "abcdefgh"):
        response = client.post(
            "/auth/register",
            data={
                "name": "Ava Applicant",
                "email": f"{password}@example.com",
                "password": password,
                "confirm_password": password,
            },
            follow_redirects=True,
        )
        assert b"Use at least 8 characters" in response.data


def test_registration_accepts_medium_two_and_strong_passwords(client):
    for index, password in enumerate(("abcdefgh12", "LongPassword1234!")):
        response = client.post(
            "/auth/register",
            data={
                "name": "Ava Applicant",
                "email": f"ava{index}@example.com",
                "password": password,
                "confirm_password": password,
            },
            follow_redirects=True,
        )
        assert b"Account created. You can now log in." in response.data


def test_registration_accepts_a_long_passphrase(client):
    password = "river maple orbit velvet candle"
    response = client.post(
        "/auth/register",
        data={
            "name": "Ava Applicant",
            "email": "passphrase@example.com",
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )
    assert b"Account created. You can now log in." in response.data


def test_settings_can_change_name_and_password(app, client):
    register(client, "Ava Applicant", "ava@example.com")
    login(client, "ava@example.com")

    response = client.post(
        "/auth/settings",
        data={"settings_action": "name", "name": "Ava Updated"},
        follow_redirects=True,
    )
    assert b"Name updated." in response.data

    response = client.post(
        "/auth/settings",
        data={
            "settings_action": "password",
            "current_password": "wrong-password",
            "new_password": "abcdefgh12",
            "confirm_password": "abcdefgh12",
        },
        follow_redirects=True,
    )
    assert b"Current password is incorrect." in response.data

    response = client.post(
        "/auth/settings",
        data={
            "settings_action": "password",
            "current_password": "LongPassword123!",
            "new_password": "abcdefgh12",
            "confirm_password": "abcdefgh12",
        },
        follow_redirects=True,
    )
    assert b"Password changed." in response.data

    client.get("/auth/logout")
    assert b"Invalid email or password" in login(
        client, "ava@example.com", "LongPassword123!"
    ).data
    assert b"Logout" in login(client, "ava@example.com", "abcdefgh12").data


def test_settings_can_delete_account(app, client):
    register(client, "Ava Applicant", "ava@example.com")
    login(client, "ava@example.com")

    response = client.post(
        "/auth/settings",
        data={"settings_action": "delete", "password": "LongPassword123!"},
        follow_redirects=True,
    )
    assert b"Your account has been deleted." in response.data
    assert b"Register" in response.data
    with app.app_context():
        assert User.query.filter_by(email="ava@example.com").first() is None
