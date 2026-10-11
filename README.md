# Dialogue Service API

[![API and worker tests](https://github.com/andreystashev/dialogue-service-api/actions/workflows/tests.yml/badge.svg)](https://github.com/andreystashev/dialogue-service-api/actions/workflows/tests.yml)

A **FastAPI backend** with user authentication, asynchronous dialogue jobs, and persistent result history. Built as part of the *Programming Practice* course at the National University of Science and Technology MISIS.

The current dialogue implementation returns a random joke from a local list. It demonstrates the request → background task → stored result workflow; it does not call a language model.

## Features

- User registration, administrator activation, and password changes.
- JWT sign-in, token refresh, and logout.
- Celery jobs with Redis as broker and result backend.
- PostgreSQL history, cached prompt results, and paginated history endpoints.
- Request rate limiting, response timing, and Prometheus instrumentation.
- OpenAPI documentation and Alembic database migrations.

## Architecture

```text
Client → FastAPI → Celery / Redis → worker → PostgreSQL
            └────────── history and result lookup ─────┘
```

The worker checks for a cached prompt, otherwise selects a local joke, then stores the user's result. Database sessions close after success, a cache return, or an exception.

| Component | Responsibility |
| --- | --- |
| [app/api/api_v1/](app/api/api_v1/) | Authentication, users, dialogue, and health routes |
| [app/services/](app/services/) | User, token, history, and worker logic |
| [app/db/](app/db/) | SQLAlchemy models and repositories |
| [app/core/config.py](app/core/config.py) | Environment configuration |
| [app/get_jokes/get_jokes.py](app/get_jokes/get_jokes.py) | Current local joke implementation |
| [migrations/](migrations/) | Alembic migrations |
| [tests/](tests/) | Unit and database-backed API tests |

## Run the API and worker

Requirements: **Docker Engine/Desktop and Compose v2**. The application image uses Python 3.10.

```bash
git clone https://github.com/andreystashev/dialogue-service-api.git
cd dialogue-service-api
cp .env.example .env
```

Edit `.env`: set `APP_PORT=8080`, replace the example secret and database password, and retain the Compose database/Redis hostnames. Leave the unused OpenAI variables present; settings validation currently requires them even though the local joke implementation does not use them.

Build the application, start its backing services, apply migrations, and start the API:

```bash
docker compose build dialog-api
docker compose up -d postgres redis
docker compose run --rm dialog-api alembic upgrade head
docker compose up -d dialog-api
```

Start a worker in a second terminal with the Celery 5 command format:

```bash
docker compose run --rm --no-deps worker celery --app=app.services.worker_svc:celery_app worker -l info -Q default
```

Open **<http://localhost:8080/docs>** for interactive documentation. The root URL redirects there, and the live schema is available at `/openapi.json`. A snapshot is committed as [openapi.yaml](openapi.yaml).

The worker command above runs in the foreground; Ctrl+C stops it. Use `docker compose down` to stop the API, PostgreSQL, and Redis while preserving named volumes.

The full legacy Compose stack also defines Flower and a separate joke container. Its default worker command predates the Celery 5 dependency update. The steps above explicitly select the API/database/Redis services and override that worker command; do not use plain `docker compose up` as a verified full-stack launch. The worker already imports the joke function directly, so no separate joke image is needed for this workflow.

## API workflow

Register a user, have an administrator activate it, then sign in using the email as the OAuth2 form's `username`. The repository does not automatically provision an initial administrator.

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/api/v1/users/user/` | Register a user |
| PUT | `/api/v1/users/activate/{user_id}` | Administrator activation |
| POST | `/api/v1/auth/sign_in` | Obtain an access token |
| POST | `/api/v1/auth/refresh_token` | Refresh a token |
| POST | `/api/v1/auth/logout` | Disable the current token |
| PUT | `/api/v1/users/set_password` | Change your password |
| POST | `/api/v1/dialog/create` | Submit a background job |
| GET | `/api/v1/dialog/status/{dialog_id}` | Poll task status |
| GET | `/api/v1/dialog/result/{dialog_id}` | Retrieve the stored result |
| GET | `/api/v1/dialog/history` | Paginated user history |
| GET | `/api/v1/healthcheck` | API health |

Password changes require a Bearer token and a JSON body:

```http
PUT /api/v1/users/set_password
Authorization: Bearer <access-token>
Content-Type: application/json

{"password": "new-password", "password_confirm": "new-password"}
```

Password query parameters are no longer supported. Update older clients to JSON. Validation responses do not copy the original request body, and password-change model fields use masked secret values; length and confirmation rules remain in the user service.

## Development and tests

Use **Python 3.10** and the compatible test dependencies:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install pip==24.0
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests/unit -v
```

Unit tests supply isolated settings and replace database dependencies. They need no PostgreSQL, Redis, or running worker. They cover password JSON input, authorization, validation responses, and database-session cleanup in worker success/cache/error paths.

GitHub Actions additionally runs `python -m pytest tests/app -q` against a disposable PostgreSQL database. **These integration tests recreate tables**: use a separate test database such as `dialogue_test`, never a working database. See the [workflow](.github/workflows/tests.yml) for the exact service and environment setup.

This is an educational backend using an older FastAPI/Pydantic stack. CI checks the API and worker logic; it does not validate the complete legacy Compose deployment or an external generation service.
