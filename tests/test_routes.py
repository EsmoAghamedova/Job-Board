import io
import json
import logging

from urllib.error import URLError

from app.main import routes as main_routes


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
        "password": "LongPassword123!",
        "confirm_password": "LongPassword123!",
    })
    assert response.status_code == 400


def test_server_error_page_is_rendered_and_logged(app, client, caplog):
    app.config.update(TESTING=False, PROPAGATE_EXCEPTIONS=False)

    def raise_error():
        raise RuntimeError("test failure")

    app.add_url_rule("/test-error", view_func=raise_error)
    with caplog.at_level(logging.ERROR, logger=app.logger.name):
        response = client.get("/test-error")

    assert response.status_code == 500
    assert b"THE SERVER IS IN A MEETING" in response.data
    assert "Unhandled server error: test failure" in caplog.text


def test_external_api_success_is_rendered(app, monkeypatch):
    response_data = {"content": "Keep building.", "author": "JobBoard"}
    response = io.BytesIO(json.dumps(response_data).encode())
    monkeypatch.setattr(main_routes, "urlopen", lambda url, timeout: response)

    with app.app_context():
        quote = main_routes.get_quote()

    assert quote == response_data


def test_external_api_error_uses_fallback_and_logs(app, monkeypatch, caplog):
    monkeypatch.setattr(
        main_routes,
        "urlopen",
        lambda url, timeout: (_ for _ in ()).throw(URLError("offline")),
    )

    with app.app_context(), caplog.at_level(logging.WARNING, logger=app.logger.name):
        quote = main_routes.get_quote()

    assert quote["author"] == "JobBoard"
    assert "API request error" in caplog.text
