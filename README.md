# University Results API

A small university management backend built with Django REST Framework. The scope is deliberately narrow: students look up their grades, enroll in courses, and professors manage grades for the courses they teach. The point of the project is not the number of features, it is how the system behaves when a lot of people use it at the same time.

Every university portal has the same bad day: results get published, thousands of students open the site at once, and it crawls or falls over. Enrollment has its own version of this, where two students click "enroll" on the last seat in a course at the same moment. This project is my attempt to handle both problems properly and to measure the result instead of just claiming it works.

> **Status:** work in progress. The environment and database are set up; the application itself is being built phase by phase. See the [roadmap](#roadmap) for where things stand.

## What it does

**Students**
- View their own grades (read-only; the results endpoint only accepts `GET`)
- View their own profile
- Enroll in courses

**Professors**
- Set the capacity of the courses they teach
- Create and update grades for students in those courses
- See only a student's ID, name and grade. No other personal data is exposed to this role.

**Admins**
- Full access to everything

## The interesting problems

### 1. Traffic spikes on the results endpoint
The app is a single Django codebase (a monolith), and that does not rule out scaling it. Running several identical copies of the app behind a reverse proxy works as long as the app is stateless, so this project uses JWT authentication and keeps shared state in Redis rather than in process memory.

Three layers are used to keep the server responsive under load:
- **Caching:** grades are cached per student in Redis and invalidated whenever a professor changes a grade. Responses are never cached across users.
- **Rate limiting:** Nginx limits raw request rates at the edge, and DRF throttling applies per-user limits (stricter on the enrollment endpoint).
- **Load balancing:** Nginx distributes requests across multiple Gunicorn instances of the same app.

### 2. Enrolling in the last seat
If a course has one seat left and two students submit at the same time, a naive "check, then insert" can let both through. The enrollment endpoint avoids this with database-level concurrency control:
- The work happens inside `transaction.atomic()`
- The course row is locked with `select_for_update()`, so concurrent requests are serialized
- A unique constraint on `(student, course)` prevents duplicate enrollments

The endpoint returns `201` on success, `409` if the course is full, and `400` for a duplicate enrollment. A concurrency test fires many parallel requests at a one-seat course and asserts that exactly one succeeds.

### 3. Grade auditing
Every grade change is recorded with who made it and when, using `django-simple-history`.

## Tech stack

| Area | Tool |
|---|---|
| Framework | Django, Django REST Framework |
| Database | PostgreSQL |
| Cache / throttle store | Redis (`django-redis`) |
| Auth | JWT via `djangorestframework-simplejwt` |
| App server | Gunicorn |
| Reverse proxy / load balancer | Nginx |
| Background jobs (optional, for a waitlist) | Celery |
| API docs | `drf-spectacular` |
| Audit trail | `django-simple-history` |
| Testing | `pytest`, `pytest-django`, `factory_boy` |
| Load testing | Locust |

## Getting started

These steps assume Ubuntu, either native or through WSL2 on Windows. Gunicorn, Redis and Nginx do not run natively on Windows, so WSL2 is the easiest route there.

### Prerequisites
- Python 3.12
- PostgreSQL
- Redis
- Nginx

```bash
sudo apt update
sudo apt install -y python3-venv python3-dev libpq-dev postgresql postgresql-contrib redis-server nginx
sudo service postgresql start
sudo service redis-server start
```

### Installation

```bash
git clone <your-repo-url>
cd uni
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database

```bash
sudo -u postgres psql
```

```sql
CREATE USER uni_user WITH PASSWORD 'choose_a_password';
CREATE DATABASE uni_db OWNER uni_user;
\q
```

### Environment variables

Create a `.env` file in the same folder as `manage.py` (the inner `uni/` directory):

```
SECRET_KEY=replace-with-a-long-random-string
DEBUG=True
DB_NAME=uni_db
DB_USER=uni_user
DB_PASSWORD=choose_a_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

You can generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

The `.env` file is listed in `.gitignore` and should never be committed.

### Run it

```bash
cd uni            # the folder that contains manage.py
python manage.py migrate
python manage.py runserver
```

## Project layout

```
uni/
├── uni/                 Django project root
│   ├── manage.py
│   ├── .env             local settings (not in git)
│   ├── core/            application code
│   └── uni/             settings, urls, wsgi/asgi
├── requirements.txt
└── README.md
```

## Roadmap

- [x] **Phase 0:** environment, PostgreSQL connection, settings loaded from `.env`
- [ ] **Phase 1:** custom user model with roles, core models, JWT login
- [ ] **Phase 2:** role-based permissions and the read-only results endpoint
- [ ] **Phase 3:** grade management for professors, audit history, API docs
- [ ] **Phase 4:** enrollment with row locking and a concurrency test
- [ ] **Phase 5:** per-student caching with invalidation
- [ ] **Phase 6:** rate limiting in DRF and Nginx
- [ ] **Phase 7:** multiple Gunicorn instances behind Nginx
- [ ] **Phase 8:** load tests and benchmarks
- [ ] **Phase 9:** cleanup, indexes, final documentation

## Benchmarks

To be filled in once Phase 8 is done. The plan is to compare each of these and report requests per second, p95 latency and error rate:

| Scenario | Req/s | p95 latency | Error rate |
|---|---|---|---|
| Results endpoint, no cache | | | |
| Results endpoint, Redis cache | | | |
| 1 Gunicorn instance | | | |
| 3 instances behind Nginx | | | |
| Flood with rate limiting off | | | |
| Flood with rate limiting on | | | |

## Running the tests

```bash
pytest
```

Concurrency tests use `TransactionTestCase`, because the standard `TestCase` wraps each test in a transaction and would hide the locking behaviour being tested.

## Notes and decisions

- Docker is intentionally left out for now. The goal is to understand each piece (Postgres, Redis, Gunicorn, Nginx) running directly before wrapping it in containers.
- A priority queue is not used for the last-seat problem, since the row lock already gives first-come, first-served ordering. A waitlist with a background job is a possible later addition.

## License

MIT
