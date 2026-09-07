import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask, render_template

from config import Config
from app.extensions import db, migrate, login_manager, csrf
from app.models import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.jobs.routes import jobs_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")

    configure_logging(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    return app


def configure_logging(app):
    if any(isinstance(handler, RotatingFileHandler) for handler in app.logger.handlers):
        return
    os.makedirs(os.path.join(app.root_path, "..", "logs"), exist_ok=True)
    handler = RotatingFileHandler(os.path.join(
        app.root_path, "..", "logs", "app.log"), maxBytes=1024 * 1024, backupCount=5)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s"))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
