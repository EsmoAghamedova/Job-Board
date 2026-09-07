import os
import uuid
from datetime import datetime, timezone

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_from_directory, url_for)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.jobs.forms import ApplicationForm, JobForm
from app.models import Application, Category, Job, Notification

jobs_bp = Blueprint("jobs", __name__)


def prepare_job_form(form, job=None):
    categories = Category.query.order_by(Category.name).all()
    form.category.choices = [(category.id, category.name)
                             for category in categories]
    if job is not None and request.method == "GET":
        form.category.data = job.category_id
    return form


def populate_job_fields(form, job):
    for field_name in ("title", "short_description", "full_description",
                       "company", "salary", "location"):
        setattr(job, field_name, getattr(form, field_name).data)
    job.category_id = form.category.data


@jobs_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_job():
    form = prepare_job_form(JobForm())
    if form.validate_on_submit():
        job = Job(user_id=current_user.id)
        populate_job_fields(form, job)
        db.session.add(job)
        db.session.commit()
        current_app.logger.info(
            "New job created: %s by %s", job.id, current_user.email)
        flash("Job posted.", "success")
        return redirect(url_for("main.home"))
    return render_template("jobs/job_form.html", form=form, heading="Add a job")


@jobs_bp.route("/<int:job_id>")
def detail(job_id):
    job = db.get_or_404(Job, job_id)
    application = None
    if current_user.is_authenticated:
        application = Application.query.filter_by(
            job_id=job.id, applicant_id=current_user.id).first()
    return render_template("jobs/detail.html", job=job, application=application)


@jobs_bp.route("/<int:job_id>/apply", methods=["GET", "POST"])
@login_required
def apply(job_id):
    job = db.get_or_404(Job, job_id)
    if job.user_id == current_user.id:
        abort(403)
    if Application.query.filter_by(job_id=job.id,
                                   applicant_id=current_user.id).first():
        flash("You have already applied for this role.", "info")
        return redirect(url_for("jobs.detail", job_id=job.id))
    form = ApplicationForm(obj=current_user)
    if form.validate_on_submit():
        upload_folder = current_app.config["CV_UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        original_name = secure_filename(form.cv.data.filename)
        filename = f"{uuid.uuid4().hex}_{original_name}"
        form.cv.data.save(os.path.join(upload_folder, filename))
        application = Application(
            job_id=job.id,
            applicant_id=current_user.id,
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            phone=form.phone.data.strip(),
            cv_filename=filename,
            cover_letter=form.cover_letter.data.strip(),
        )
        db.session.add(application)
        db.session.commit()
        current_app.logger.info("Application created: job=%s applicant=%s",
                                job.id, current_user.email)
        flash("Your application was sent to the company.", "success")
        return redirect(url_for("jobs.detail", job_id=job.id))
    return render_template("jobs/application_form.html", form=form, job=job)


@jobs_bp.route("/<int:job_id>/applications")
@login_required
def applications(job_id):
    job = db.get_or_404(Job, job_id)
    if job.user_id != current_user.id:
        abort(403)
    applications = Application.query.filter_by(job_id=job.id).order_by(
        Application.created_at.desc()).all()
    return render_template("jobs/applications.html", job=job,
                           applications=applications)


@jobs_bp.post("/applications/<int:application_id>/<decision>")
@login_required
def review_application(application_id, decision):
    application = db.get_or_404(Application, application_id)
    if application.job.user_id != current_user.id:
        abort(403)
    if decision not in {"approve", "reject"}:
        abort(404)
    application.status = "approved" if decision == "approve" else "rejected"
    application.reviewed_at = datetime.now(timezone.utc)
    message = f"Your application for {application.job.title} was {application.status}."
    db.session.add(Notification(user_id=application.applicant_id,
                                application_id=application.id,
                                message=message))
    db.session.commit()
    current_app.logger.info("Application %s %s by %s", application.id,
                            application.status, current_user.email)
    flash(f"Application {application.status}.", "success")
    return redirect(url_for("jobs.applications", job_id=application.job_id))


@jobs_bp.route("/applications/<int:application_id>/cv")
@login_required
def download_cv(application_id):
    application = db.get_or_404(Application, application_id)
    if current_user.id not in {application.applicant_id,
                               application.job.user_id}:
        abort(403)
    return send_from_directory(current_app.config["CV_UPLOAD_FOLDER"],
                               application.cv_filename, as_attachment=True)


@jobs_bp.route("/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit(job_id):
    job = db.get_or_404(Job, job_id)
    if job.user_id != current_user.id:
        abort(403)
    form = prepare_job_form(JobForm(obj=job), job)
    if form.validate_on_submit():
        populate_job_fields(form, job)
        db.session.commit()
        current_app.logger.info("Job modified: %s by %s",
                                job.id, current_user.email)
        flash("Job updated.", "success")
        return redirect(url_for("jobs.detail", job_id=job.id))
    return render_template("jobs/job_form.html", form=form, heading="Edit job")


@jobs_bp.post("/<int:job_id>/delete")
@login_required
def delete(job_id):
    job = db.get_or_404(Job, job_id)
    if job.user_id != current_user.id:
        abort(403)
    db.session.delete(job)
    db.session.commit()
    current_app.logger.info("Job deleted: %s by %s",
                            job.id, current_user.email)
    flash("Job deleted.", "success")
    return redirect(url_for("main.home"))
