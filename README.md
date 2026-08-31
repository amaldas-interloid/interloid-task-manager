# Interloid Task Manager

A production-oriented Task Management REST API built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **JWT authentication**.

The project focuses on secure authentication, role-based authorization, refresh-token management, user administration, and task management.


## Tech Stack

* Python 3.12+
* FastAPI
* PostgreSQL
* SQLAlchemy 2.x (Async)
* Alembic
* PyJWT
* Argon2 password hashing
* Pydantic
* Pytest
* HTTPX
* Ruff
* Mypy
* Pre-commit
* uv

---

## Current Implementation Status

### Authentication — Completed

The following authentication features are implemented:

* User registration
* User login
* JWT access token generation
* Opaque refresh tokens
* Refresh-token rotation
* Refresh-token revocation
* Logout
* Get current user (`/me`)
* Change password
* Revoke all refresh tokens after password change
* Inactive-user validation
* Password hashing using Argon2
* Dummy password verification to reduce login timing differences

### Authorization — Completed

Role-based authorization is implemented with two roles:

* `ADMIN`
* `USER`

Current authorization features include:

* Admin-only user listing
* Admin user role management
* User activation/deactivation
* Protection against admin self-demotion
* Protection against admin self-deactivation
* Protection against removing the last active admin
* Active-user validation on authenticated requests



### User

Contains:

* UUID7 ID
* Email
* Password hash
* First name
* Last name
* Role
* Active status
* Created/updated timestamps

### Refresh Token

Contains:

* UUID7 ID
* User ID
* Token hash
* Expiration time
* Revocation time
* Created/updated timestamps

### Task

Contains:

* UUID7 ID
* Owner ID
* Title
* Description
* Status
* Priority
* Due date
* Created/updated timestamps

Indexes are used on task fields needed for common queries, including:

* `owner_id`
* `status`
* `due_date`

---

## Demo Seed Data
```

### Admin

```text
Amaldas
```

### Demo Users

```text
Naveen
Vikram
Madhavan
Satheesh
Vijay
Mani
Priya
Jeffy
Saniya
```
### clone the repository
```
git clone git@github.com:amaldas-interloid/interloid-task-manager.git
```


Run the seed script with:

```bash
 uv run python scripts/seed.py
```

---

## Database Migrations

Alembic is used for schema migrations.

Check the current migration:

```bash
 uv run alembic current
```

Apply migrations:

```bash
 uv run alembic upgrade head
```

---

## Running the Application

Install dependencies:

```bash
uv sync
```

Run migrations:

```bash
 uv run alembic upgrade head
```

Optionally seed demo data:

```bash
 uv run python scripts/seed.py
```

Start the FastAPI application:

```bash
 uv run uvicorn app.main:app --reload
```

Open Swagger UI in the browser and use it to demonstrate the API endpoints.

---

## Testing

The project uses **Pytest**, **HTTPX AsyncClient**, and a separate test database.

Run tests:

```bash
ENV_FILE=.env.test uv run pytest
```

Run tests with coverage:

```bash
ENV_FILE=.env.test uv run pytest --cov=app --cov-report=term-missing
```

Authentication and authorization integration tests are implemented.


---

## Code Quality

The project uses:

* Ruff for linting and formatting
* Mypy for static type checking
* Pre-commit for automatic code-quality checks

Run Ruff:

```bash
uv run ruff check .
```

Run Mypy:

```bash
uv run mypy .
```

Run all pre-commit hooks:

```bash
uv run pre-commit run --all-files
```

Current pre-commit checks include:

```text
Trailing whitespace
End-of-file fixing
YAML validation
Ruff linting
Ruff formatting
```

---

