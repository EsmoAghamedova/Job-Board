from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    image_file = db.Column(
        db.String(120), nullable=False, default="default.jpg")
    jobs = db.relationship("Job", back_populates="author",
                           cascade="all, delete-orphan")
    applications = db.relationship("Application", back_populates="applicant",
                                   cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user",
                                    cascade="all, delete-orphan")
    saved_jobs = db.relationship("SavedJob", back_populates="user",
                                 cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    jobs = db.relationship("Job", back_populates="category")


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    short_description = db.Column(db.String(300), nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(160), nullable=False)
    salary = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        "category.id"), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", back_populates="jobs")
    category = db.relationship("Category", back_populates="jobs")
    applications = db.relationship("Application", back_populates="job",
                                   cascade="all, delete-orphan")
    saved_by = db.relationship("SavedJob", back_populates="job",
                               cascade="all, delete-orphan")


class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False,
                        index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False,
                       index=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    user = db.relationship("User", back_populates="saved_jobs")
    job = db.relationship("Job", back_populates="saved_by")
    __table_args__ = (db.UniqueConstraint("user_id", "job_id",
                                          name="unique_saved_job"),)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    applicant_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    cv_filename = db.Column(db.String(255), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime, nullable=True)
    job = db.relationship("Job", back_populates="applications")
    applicant = db.relationship("User", back_populates="applications")
    __table_args__ = (db.UniqueConstraint("job_id", "applicant_id",
                                          name="unique_job_applicant"),)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    application_id = db.Column(
        db.Integer, db.ForeignKey("application.id"), nullable=True)
    message = db.Column(db.String(300), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    user = db.relationship("User", back_populates="notifications")
