# TU Platform — Multi-College Management System

A production-ready, multi-tenant college management platform for Tribhuvan University–affiliated colleges.

**Live:** [tu-platform.onrender.com](https://tu-platform.onrender.com)

## What it does

- **Multi-tenant architecture** — every college's data is isolated at the database level
- **4 user roles** — TU Admin, College Admin, Teacher, Student — each with their own dashboard
- **Academic structure** — Departments → Programs → Semesters → Subjects
- **Attendance** — teachers mark, students see their percentage
- **Notices** — three scopes: TU-wide, college-wide, department-level
- **Marks/Results** — teachers enter marks, students see grades

## Tech stack

- **Backend:** Django 5, Python 3.13
- **Database:** PostgreSQL (production), SQLite (local dev)
- **Frontend:** Bootstrap 5, vanilla JS, Django templates
- **Deployment:** Render (Web Service + Postgres)
- **Static files:** WhiteNoise

## Features in detail

### Role-based access
| Role | Access |
|---|---|
| TU Admin | All colleges, all data |
| College Admin | Only their assigned college |
| Teacher | Only their college, their subjects, their students |
| Student | Only their own data + their college's resources |

### Multi-tenant isolation
Every model has a `college` foreign key. All queries are scoped by the authenticated user's college — enforced at the model/manager level, not just the UI.

## Local setup

```bash
git clone https://github.com/sushantcdy734/tu-platform.git
cd tu-platform
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver