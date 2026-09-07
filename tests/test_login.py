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
        data={"email": "ava@example.com", "password": "password123"},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/jobs/1/apply")
