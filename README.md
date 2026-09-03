# Interloid Task Manager

A production-oriented Task Management REST API built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **JWT authentication**.

The project focuses on secure authentication, role-based authorization, refresh-token management, user administration, task management, automated testing, and containerized deployment.

---

## Features

### Authentication

* User registration
* User login
* JWT access-token generation
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

### Authorization

Role-based authorization is implemented with two roles:

* `ADMIN`
* `USER`

Authorization features include:

* Admin-only user listing
* Admin user-role management
* User activation/deactivation
* Protection against admin self-demotion
* Protection against admin self-deactivation
* Protection against removing the last active admin
* Active-user validation on authenticated requests
* Task ownership protection
* Users can manage only their own tasks
* Admins can view and manage all users' tasks

### Task Management

Task management supports:

* Create a task
* List tasks
* Get a task by ID
* Update a task
* Delete a task
* Filter tasks by status
* Filter tasks by priority
* Filter tasks by due-date range
* Case-insensitive title search
* Limit/offset pagination
* Admin filtering by `owner_id`
* Ownership-based access control

Task ownership is determined from the authenticated user's access token and is never accepted from the task creation request body.

---

## Tech Stack

* Python 3.12+
* FastAPI
* PostgreSQL
* SQLAlchemy 2.x (Async)
* Alembic
* PyJWT
* Argon2
* Pydantic
* Pytest
* HTTPX
* Ruff
* Mypy
* Pre-commit
* uv
* Docker
* AWS EC2

---

## Data Models

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

Task indexes are used for commonly queried fields, including:

* `owner_id`
* `status`
* `due_date`

---

## Task Status and Priority

Supported task statuses:

```text
Todo
In Progress
Done
```

Supported task priorities:

```text
Low
Medium
High
```

---

## API Endpoints

### Authentication

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
PATCH  /api/v1/auth/change-password
```

### User Administration

```text
GET    /api/v1/users
PATCH  /api/v1/users/{user_id}
```

These endpoints require admin privileges.

### Tasks

```text
POST    /api/v1/tasks
GET     /api/v1/tasks
GET     /api/v1/tasks/{task_id}
PATCH   /api/v1/tasks/{task_id}
DELETE  /api/v1/tasks/{task_id}
```

The task-list endpoint supports:

```text
?owner_id=
?status=
?priority=
?due_from=
?due_to=
?search=
?limit=
?offset=
```

`owner_id` filtering is available to administrators. Normal users always receive only their own tasks.

Pagination defaults to:

```text
limit=20
offset=0
```

The maximum allowed `limit` is `100`.

---

## Clone the Repository

```bash
git clone git@github.com:interloid/interloid-task-manager.git
cd interloid-task-manager
```

---

## Environment Configuration

Create the required `.env` file before starting the application.

The application configuration includes values for:

```text
Database connection
JWT secret
JWT algorithm
Access-token expiration
Refresh-token expiration
Application environment
```

---

## Install Dependencies

The project uses `uv` for Python dependency management.

```bash
uv sync
```

---

## Database Migrations

Alembic is used for database schema migrations.

Check the current migration:

```bash
uv run alembic current
```

Apply all migrations:

```bash
uv run alembic upgrade head
```

---

## Demo Seed Data


For testing and verifying the application with seed data, refer to the `.env.example` file for the required configuration and sample credentials.


Run the seed script with:

```bash
uv run python scripts/seed.py
```

---

## Running the Application

Install dependencies:

```bash
uv sync
```

Apply database migrations:

```bash
uv run alembic upgrade head
```

Optionally seed demo data:

```bash
uv run python scripts/seed.py
```

Start the FastAPI development server:

```bash
uv run uvicorn app.main:app --reload
```

The application runs locally on port `8000` by default.

Swagger UI:

```text
http://localhost:8000/docs
```

---

## Testing

The project uses **Pytest**, **HTTPX AsyncClient**, and a separate test database for integration testing.

Run all tests:

```bash
ENV_FILE=.env.test uv run pytest
```

Run task tests:

```bash
ENV_FILE=.env.test uv run pytest tests/tasks
```

Run tests with coverage:

```bash
ENV_FILE=.env.test uv run pytest --cov=app --cov-report=term-missing
```

Test coverage includes:

* Authentication
* Refresh-token rotation and revocation
* Authorization
* User administration
* Task CRUD
* Task ownership
* Admin task access
* Task filtering
* Task search
* Task pagination
* Request validation

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

Run Ruff formatting:

```bash
uv run ruff format .
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

## Docker

### Build the Image

```bash
docker build -t interloid-task-manager:v1.1.0 .
```

### Run Locally

```bash
docker run -d \
  --name interloid-task-manager \
  --restart unless-stopped \
  --env-file .env \
  -p 8000:8000 \
  interloid-task-manager:v1.1.0
```

Check the running container:

```bash
docker ps
```

Check application logs:

```bash
docker logs interloid-task-manager
```

---

## Docker Hub

The application image can be tagged with a specific release version.

Example:

```bash
docker tag \
  interloid-task-manager:v1.1.0 \
  amaldas12345/interloid-task-manager:v1.1.0
```

Push the versioned image:

```bash
docker push amaldas12345/interloid-task-manager:v1.1.0
```

Versioned Docker tags are used so deployments can be identified and rolled back when necessary.

---

## Deployment

The application is containerized using Docker and deployed on AWS EC2.

Current release:

```text
v1.1.0
```

The deployed container exposes FastAPI through port `8000`.

Deployment flow:

```text
Source Code
    ↓
Docker Build
    ↓
Local Verification
    ↓
Docker Hub
    ↓
AWS EC2
    ↓
Docker Pull
    ↓
Container
    ↓
FastAPI :8000
```

A deployment script can be used on EC2 to pull and deploy a specific version:

```bash
./deploy.sh v1.1.0
```

This allows future versions to be deployed using the same process:

```bash
./deploy.sh v1.2.0
```

---

## API Documentation

FastAPI automatically provides interactive API documentation through Swagger UI.

For local development:

```text
http://localhost:8000/docs
```

The Swagger interface can be used to test authentication, user administration, and task-management endpoints.
