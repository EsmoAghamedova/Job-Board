import os
import shutil

import pytest

from app import create_app
from app.extensions import db
from app.models import Category


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "app/static/uploads"
    CV_UPLOAD_FOLDER = "instance/test_cv_uploads"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        db.session.add_all([Category(name=name) for name in (
            "IT", "Design", "Marketing", "Finance", "Sales", "Engineering", "Other")])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()
        shutil.rmtree(TestConfig.CV_UPLOAD_FOLDER, ignore_errors=True)


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, name, email, password="password123"):
    return client.post("/auth/register", data={"name": name, "email": email, "password": password, "confirm_password": password}, follow_redirects=True)


def login(client, email, password="password123"):
    return client.post("/auth/login", data={"email": email, "password": password}, follow_redirects=True)


def category_id(name="IT"):
    return Category.query.filter_by(name=name).one().id
