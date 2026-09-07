from io import BytesIO

from app.extensions import db
from app.models import Application, Job, Notification
from tests.conftest import category_id, login, register


def test_users_cannot_edit_or_delete_another_users_job(app, client):
    register(client, "Owner", "owner@example.com")
    login(client, "owner@example.com")
    with app.app_context():
        job = Job(title="Private role", short_description="A role", full_description="Details",
                  company="Acme", salary="100k", location="Tbilisi", category_id=category_id(), user_id=1)
        db.session.add(job)
        db.session.commit()
        job_id = job.id
    client.get("/auth/logout")
    register(client, "Visitor", "visitor@example.com")
    login(client, "visitor@example.com")
    assert client.get(f"/jobs/{job_id}/edit").status_code == 403
    assert client.post(f"/jobs/{job_id}/delete").status_code == 403


def test_job_owner_reviews_application_and_applicant_gets_notification(app, client):
    register(client, "Owner", "owner@example.com")
    login(client, "owner@example.com")
    with app.app_context():
        owner_id = 1
        job = Job(title="Python role", short_description="A role", full_description="Details",
                  company="Acme", salary="100k", location="Tbilisi", category_id=category_id(), user_id=owner_id)
        db.session.add(job)
        db.session.commit()
        job_id = job.id
    client.get("/auth/logout")
    register(client, "Applicant", "applicant@example.com")
    login(client, "applicant@example.com")
    response = client.post(f"/jobs/{job_id}/apply", data={"name": "Applicant", "email": "applicant@example.com", "phone": "555-0100",
                           "cover_letter": "I would love to join this team and contribute.", "cv": (BytesIO(b"cv contents"), "resume.pdf")}, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        application_id = Application.query.one().id
    client.get("/auth/logout")
    login(client, "owner@example.com")
    assert client.post(
        f"/jobs/applications/{application_id}/approve", follow_redirects=True).status_code == 200
    with app.app_context():
        assert Application.query.one().status == "approved"
        assert Notification.query.one().message.endswith("approved.")
    client.get("/auth/logout")
    login(client, "applicant@example.com")
    assert b"approved" in client.get("/auth/notifications").data


def test_owner_can_delete_own_job(app, client):
    register(client, "Owner", "owner@example.com")
    login(client, "owner@example.com")
    with app.app_context():
        job = Job(title="Temporary role", short_description="A role", full_description="Details",
                  company="Acme", salary="100k", location="Tbilisi", category_id=category_id(), user_id=1)
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    response = client.post(f"/jobs/{job_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert db.session.get(Job, job_id) is None
