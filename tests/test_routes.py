def test_public_routes_and_missing_page(client):
    assert client.get("/").status_code == 200
    assert client.get("/about").status_code == 200
    assert client.get("/auth/profile").status_code == 302
    assert client.get("/does-not-exist").status_code == 404


def test_missing_csrf_token_is_rejected(app, client):
    app.config["WTF_CSRF_ENABLED"] = True
    response = client.post("/auth/register", data={
        "name": "No Token",
        "email": "no-token@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    assert response.status_code == 400
