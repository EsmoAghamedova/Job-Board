from datetime import datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.models import Category, Job, User


CATEGORY_NAMES = ["IT", "Design", "Marketing",
                  "Finance", "Sales", "Engineering", "Other"]


DEMO_USERS = [
    {
        "name": "Mariam Beridze",
        "email": "mariam.demo@jobboard.local",
        "password": "Demo123!",
    },
    {
        "name": "Giorgi Maisuradze",
        "email": "giorgi.demo@jobboard.local",
        "password": "Demo123!",
    },
    {
        "name": "Nino Kapanadze",
        "email": "nino.demo@jobboard.local",
        "password": "Demo123!",
    },
]

DEMO_JOBS = [
    {
        "title": "Product Designer",
        "short_description": "Shape simple, useful experiences for a growing digital product.",
        "full_description": "Work with product and engineering teams to turn research into clear, accessible interfaces. You will own design from early sketches through launch and help the team build a stronger design culture.",
        "company": "Northstar Studio",
        "salary": "$1,800 - $2,400",
        "location": "Tbilisi / Hybrid",
        "category": "Design",
        "author_email": "mariam.demo@jobboard.local",
        "days_ago": 1,
    },
    {
        "title": "Backend Python Engineer",
        "short_description": "Build reliable Flask services for teams working across Europe.",
        "full_description": "Join a small backend team working on APIs, data workflows, and internal tools. We value readable Python, thoughtful testing, and engineers who enjoy making complex systems easier to use.",
        "company": "Atlas Systems",
        "salary": "$2,200 - $3,000",
        "location": "Tbilisi / Remote",
        "category": "IT",
        "author_email": "giorgi.demo@jobboard.local",
        "days_ago": 2,
    },
    {
        "title": "Content Marketing Lead",
        "short_description": "Give an ambitious education brand a sharper voice.",
        "full_description": "Own our editorial calendar, campaign stories, and community content. You will work closely with founders and subject-matter experts to turn useful ideas into content people want to share.",
        "company": "Bright Path",
        "salary": "$1,400 - $2,000",
        "location": "Tbilisi",
        "category": "Marketing",
        "author_email": "nino.demo@jobboard.local",
        "days_ago": 4,
    },
    {
        "title": "Operations Coordinator",
        "short_description": "Keep a fast-moving team organized, focused, and connected.",
        "full_description": "Coordinate schedules, improve internal processes, and support a team that works across several time zones. This role is ideal for a detail-oriented person who likes turning plans into progress.",
        "company": "Common Ground",
        "salary": "$1,200 - $1,700",
        "location": "Batumi / Hybrid",
        "category": "Other",
        "author_email": "mariam.demo@jobboard.local",
        "days_ago": 6,
    },
]


def seed():
    app = create_app()
    with app.app_context():
        users = {}
        categories = {}
        for name in CATEGORY_NAMES:
            category = Category.query.filter_by(name=name).first()
            if category is None:
                category = Category(name=name)
                db.session.add(category)
                db.session.flush()
            categories[name] = category
        for data in DEMO_USERS:
            user = User.query.filter_by(email=data["email"]).first()
            if user is None:
                user = User(name=data["name"], email=data["email"])
                user.set_password(data["password"])
                db.session.add(user)
                db.session.flush()
                print(f"Created user: {user.email}")
            else:
                print(f"User already exists: {user.email}")
            users[user.email] = user

        for data in DEMO_JOBS:
            author = users[data["author_email"]]
            existing = Job.query.filter_by(
                title=data["title"], company=data["company"], user_id=author.id
            ).first()
            if existing is None:
                job = Job(
                    title=data["title"],
                    short_description=data["short_description"],
                    full_description=data["full_description"],
                    company=data["company"],
                    salary=data["salary"],
                    location=data["location"],
                    category=categories[data["category"]],
                    user_id=author.id,
                    date_posted=datetime.now(
                        timezone.utc) - timedelta(days=data["days_ago"]),
                )
                db.session.add(job)
                print(f"Created job: {job.title}")
            else:
                print(f"Job already exists: {existing.title}")

        db.session.commit()
        print("Mock data seed complete.")


if __name__ == "__main__":
    seed()
