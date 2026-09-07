import json
import logging
from urllib.error import URLError
from urllib.request import urlopen

from flask import Blueprint, current_app, render_template, request

from app.extensions import db
from app.models import Category, Job

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    category = request.args.get("category", "").strip()
    query = Job.query.order_by(Job.date_posted.desc())
    if category:
        query = query.join(Job.category).filter(Category.name == category)
    jobs = query.all()
    categories = [value[0] for value in db.session.query(
        Category.name).order_by(Category.name).all()]
    quote = get_quote()
    return render_template("main/home.html", jobs=jobs, categories=categories, selected_category=category, quote=quote)


@main_bp.route("/about")
def about():
    return render_template("main/about.html")


def get_quote():
    try:
        with urlopen("https://api.quotable.io/random", timeout=3) as response:
            data = json.load(response)
            return {"content": data.get("content", "Build something useful."), "author": data.get("author", "Unknown")}
    except (URLError, TimeoutError, ValueError, OSError) as error:
        current_app.logger.warning("API request error: %s", error)
        return {"content": "Great work starts with a useful idea.", "author": "JobBoard"}
