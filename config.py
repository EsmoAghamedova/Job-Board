import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    running_on_render = os.environ.get("RENDER", "").lower() == "true"
    if running_on_render and not url.startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
        raise RuntimeError(
            "DATABASE_URL must be configured with a PostgreSQL URL on Render")
    url = url or "sqlite:///app.db"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql+psycopg://") and "sslmode=" not in url:
        url += "&sslmode=require" if "?" in url else "?sslmode=require"
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY and os.environ.get("FLASK_ENV") == "production":
        raise RuntimeError("SECRET_KEY must be configured in production")
    SECRET_KEY = SECRET_KEY or "dev-secret-key-change-me"
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    CV_UPLOAD_FOLDER = os.path.join(basedir, "instance", "cv_uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
