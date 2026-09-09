import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import Blueprint, current_app, jsonify, render_template, request
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Category, Job

main_bp = Blueprint("main", __name__)
QUOTE_CACHE_SECONDS = 300
_quote_cache = None
_quote_cached_at = 0.0


@main_bp.route("/")
def home():
    category = request.args.get("category", "").strip()
    search = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    sort = request.args.get("sort", "newest").strip()
    query = Job.query
    if category:
        query = query.join(Job.category).filter(Category.name == category)
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(
            Job.title.ilike(pattern),
            Job.company.ilike(pattern),
            Job.location.ilike(pattern),
            Job.short_description.ilike(pattern),
            Job.full_description.ilike(pattern),
        ))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if sort == "oldest":
        query = query.order_by(Job.date_posted.asc())
    else:
        sort = "newest"
        query = query.order_by(Job.date_posted.desc())
    jobs = query.all()
    categories = [value[0] for value in db.session.query(
        Category.name).order_by(Category.name).all()]
    quote = get_quote()
    return render_template(
        "main/home.html",
        jobs=jobs,
        categories=categories,
        selected_category=category,
        search=search,
        location=location,
        sort=sort,
        quote=quote,
    )


@main_bp.route("/about")
def about():
    return render_template("main/about.html")


@main_bp.get("/healthz")
def healthz():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify(status="ok"), 200
    except SQLAlchemyError as error:
        db.session.rollback()
        current_app.logger.error("Health check database error: %s", error)
        return jsonify(status="error"), 503


def get_quote():
    global _quote_cache, _quote_cached_at
    if _quote_cache is not None and time.monotonic() - _quote_cached_at < QUOTE_CACHE_SECONDS:
        return _quote_cache
    try:
        request = Request(
            "https://dummyjson.com/quotes/random",
            headers={"User-Agent": "JobBoard"},
        )
        with urlopen(request, timeout=3) as response:
            data = json.load(response)
            _quote_cache = {
                "content": data.get("quote", "Build something useful."),
                "author": data.get("author", "JobBoard"),
            }
    except (URLError, TimeoutError, ValueError, OSError) as error:
        current_app.logger.warning("API request error: %s", error)
        _quote_cache = {
            "content": "Great work starts with a useful idea.",
            "author": "JobBoard",
        }
    _quote_cached_at = time.monotonic()
    return _quote_cache
