import os
import uuid
from urllib.parse import urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from app.auth.forms import LoginForm, ProfileForm, RegistrationForm
from app.extensions import db
from app.models import Notification, User

auth_bp = Blueprint("auth", __name__)


def safe_next_url(value):
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or not value.startswith("/"):
        return None
    return value


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "danger")
        else:
            user = User(name=form.name.data.strip(), email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            current_app.logger.info(
                "Successful authentication: %s", user.email)
            return redirect(safe_next_url(request.args.get("next")) or url_for("main.home"))
        current_app.logger.warning(
            "Failed authentication: %s", form.email.data)
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        existing = User.query.filter(User.email == form.email.data.lower(
        ).strip(), User.id != current_user.id).first()
        if existing:
            flash("That email is already in use.", "danger")
        else:
            current_user.name = form.name.data.strip()
            current_user.email = form.email.data.lower().strip()
            if form.picture.data:
                original_name = secure_filename(form.picture.data.filename)
                filename = f"{uuid.uuid4().hex}_{original_name}"
                form.picture.data.save(os.path.join(
                    current_app.config["UPLOAD_FOLDER"], filename))
                current_user.image_file = filename
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form)


@auth_bp.route("/profile/<int:user_id>")
def public_profile(user_id):
    user = db.get_or_404(User, user_id)
    return render_template("auth/public_profile.html", user=user)


@auth_bp.route("/notifications")
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()).all()
    for notification in user_notifications:
        notification.is_read = True
    db.session.commit()
    return render_template("auth/notifications.html", notifications=user_notifications)
