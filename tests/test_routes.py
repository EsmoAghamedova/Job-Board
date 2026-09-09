import io
import json
import logging

from urllib.error import URLError

from app.main import routes as main_routes
from app.extensions import db
from app.models import Category, Job, User
from tests.conftest import login, register


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
    main_routes._quote_cache = None
    response = io.BytesIO(
        b'{"quote": "Keep building.", "author": "DummyJSON"}')
    monkeypatch.setattr(main_routes, "urlopen",
                        lambda request, timeout: response)

    with app.app_context():
        quote = main_routes.get_quote()

    assert quote == {"content": "Keep building.", "author": "DummyJSON"}


def test_external_api_error_uses_fallback_and_logs(app, monkeypatch, caplog):
    main_routes._quote_cache = None
    monkeypatch.setattr(
        main_routes,
        "urlopen",
        lambda request, timeout: (_ for _ in ()).throw(URLError("offline")),
    )

    with app.app_context(), caplog.at_level(logging.WARNING, logger=app.logger.name):
        quote = main_routes.get_quote()

    assert quote["author"] == "JobBoard"
    assert "API request error" in caplog.text


def test_health_check_reports_database_status(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_home_search_and_location_filters(app, client, monkeypatch):
    monkeypatch.setattr(main_routes, "get_quote", lambda: {
        "content": "Test quote", "author": "Test"
    })
    with app.app_context():
        author = User(name="Job Author", email="author@example.com")
        author.set_password("LongPassword123!")
        category = Category.query.filter_by(name="IT").one()
        db.session.add(author)
        db.session.flush()
        db.session.add(Job(
            title="Python Engineer",
            short_description="Build APIs",
            full_description="Build useful APIs",
            company="North Star",
            salary="$100k",
            location="Tbilisi",
            category_id=category.id,
            user_id=author.id,
        ))
        db.session.add(Job(
            title="Designer",
            short_description="Shape products",
            full_description="Shape useful products",
            company="Remote Studio",
            salary="$90k",
            location="Remote",
            category_id=category.id,
            user_id=author.id,
        ))
        db.session.commit()

    response = client.get("/?q=Python&location=Tbilisi")

    assert b"Python Engineer" in response.data
    assert b"Designer" not in response.data


def test_saved_jobs_are_private_and_toggle(app, client):
    with app.app_context():
        owner = User(name="Owner", email="owner@example.com")
        owner.set_password("LongPassword123!")
        db.session.add(owner)
        db.session.flush()
        job = Job(
            title="Saved Role",
            short_description="A role worth saving",
            full_description="A detailed role",
            company="Company",
            salary="$80k",
            location="Tbilisi",
            category_id=Category.query.filter_by(name="IT").one().id,
            user_id=owner.id,
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    register(client, "Candidate", "candidate@example.com")
    login(client, "candidate@example.com")
    response = client.post(f"/jobs/{job_id}/save", follow_redirects=True)

    assert b"Job saved for later." in response.data
    assert b"Saved jobs" in client.get("/auth/saved-jobs").data
    assert b"Dashboard" in client.get("/auth/dashboard").data

    response = client.post(
        f"/jobs/{job_id}/save",
        data={"next": "/auth/saved-jobs"},
        follow_redirects=True,
    )
    assert b"Job removed from your saved jobs." in response.data
