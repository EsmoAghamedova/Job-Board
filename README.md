# JobBoard 💼

A full-stack job listing web application built with **Flask**. Users can register, browse job postings, add their own listings, and manage their profile — with role-based permissions ensuring users can only edit or delete their own posts.

> Final project — Tbilisi School of Communication, Python course

---

## ✨ Features

- **Authentication & Authorization**
  - User registration with password confirmation and hashing
  - Login / logout
  - Guests can only browse jobs and view the About page
  - Authenticated users get access to Add Job, Profile, and Logout
  - Users can only edit/delete their **own** job posts; other users' posts are view-only

- **Job Listings**
  - Create, read, update, and delete (CRUD) job postings
  - Each job includes: title, short description, full description, company, salary, location, category, and author
  - Card-style job list showing title, author, date, and short description
  - "Read More" view with full job details
  - Sorting by date added
  - Filtering by category (IT, Design, Marketing, etc.)

- **User Profile**
  - Profile picture, name, and email
  - Editable profile information

- **Applications and Notifications**
  - Candidates can apply with contact details, a CV, and a cover message
  - Job owners can review, approve, or reject applications
  - Applicants receive approval/rejection notifications
  - CV downloads are protected by applicant/job-owner authorization

- **External API Integration**
  - At least one external API integrated, with data rendered dynamically through Flask

- **Forms & Security**
  - All forms protected with CSRF tokens (Flask-WTF)
  - Passwords stored using secure hashing (never in plain text)

- **Error Handling**
  - Custom, styled 404 (Not Found) and 500 (Server Error) pages

- **Logging**
  - File-based logging via Python's `logging` module, capturing:
    - Successful logins
    - Failed login attempts
    - New job entries
    - Job edits / deletions
    - External API request errors

- **Testing**
  - Unit tests written with `pytest`, covering:
    - Route accessibility
    - Login functionality
    - Authorization (preventing edits/deletes of other users' posts)

---

## 🛠 Tech Stack

| Layer          | Technology              |
|----------------|-------------------------|
| Backend        | Flask (Python)           |
| Templating     | Jinja2                   |
| Forms          | Flask-WTF                |
| Database       | SQLAlchemy (SQLite / other) |
| Auth           | Flask-Login + password hashing |
| Styling        | Bootstrap               |
| Testing        | Pytest                   |
| Logging        | Python `logging` module  |

---

## 📁 Project Structure

```
jobboard/
├── app/
│   ├── __init__.py          # App factory: extensions, blueprints, logging, error handlers
│   ├── extensions.py        # db, migrate, login_manager, csrf instances
│   ├── models.py            # User, Job, Application, Notification models
│   ├── main/                 # Home (job list) + About
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── auth/                 # Register, login, logout, profile view/edit
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── jobs/                  # Job CRUD (add, edit, delete, detail view)
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── main/
│   │   ├── jobs/
│   │   ├── auth/
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   └── static/
│       ├── css/
│       └── uploads/          # profile pictures only
├── instance/
│   └── cv_uploads/           # private CV files, not publicly served
├── tests/
│   ├── test_routes.py
│   ├── test_login.py
│   └── test_permissions.py
├── logs/
│   └── app.log
├── migrations/                # committed Flask-Migrate revisions
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/jobboard.git
cd jobboard

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
```

You can start from `.env.example` and replace the placeholder values. Never commit `.env`.

### Supabase Database

Local development uses SQLite. The deployed app uses Supabase PostgreSQL through SQLAlchemy. In Supabase, open **Project Settings → Database → Connect**, copy the transaction pooler connection string, and set it as `DATABASE_URL` in Render. The app converts `postgres://` or `postgresql://` to the `psycopg` SQLAlchemy driver and adds `sslmode=require` automatically.

### Database Setup

```bash
flask db upgrade
```

The repository includes the initial migration revision. On a new environment, run `flask db upgrade` before starting the application or loading demo data. Render runs this automatically through `render.yaml`.

### Run the App

```bash
python run.py
```

The app will be available at `http://127.0.0.1:5000`.

---

## 🧪 Running Tests

```bash
pytest tests/
```

Includes at least:

1. A route accessibility test
2. A login test
3. A permissions test (verifying users can't edit/delete others' posts)

---

## 📝 Logging

All key events are logged to `logs/app.log`, including successful/failed logins, job creation and edits, and external API errors — useful for debugging and auditing.

## 🌱 Demo Data

Populate a local database with repeatable demo users and jobs:

```bash
python seed.py
```

Demo login: `mariam.demo@mail.com` / `Mariam1234!`

---

## 🌐 Deployment

This project is deployed and publicly accessible at:

**Live URL:** [JobBoard](https://job-board-1fwu.onrender.com/)

Hosted on: `Render`

Deployment files are included in `Procfile` and `render.yaml`. Configure `SECRET_KEY` and `DATABASE_URL` in the hosting provider before deploying.

---

## 👤 Author

**Esmira Aghamedova**
Tbilisi School of Communication — Python (Backend) Course, Final Project

---

## 📄 License

This project was created for educational purposes as part of a final course assignment.
