# AI-Powered E-commerce Customer Support Platform

A full-stack e-commerce support application that combines a customer portal, staff dashboard, AI-assisted ticket conversations, policy retrieval, refund validation, and human review for high-value cases.

> **Demo data only:** seeded accounts and orders are fictional. Refund actions create application records; they do not move money or connect to a payment processor.

## Features

- Customer registration and JWT login.
- Customer order, ticket, message, and refund views.
- AI support agent with deterministic mock mode and optional Gemini provider.
- Policy retrieval over the local return-policy document using TF-IDF.
- Backend-enforced refund validation, return windows, idempotency, and high-value escalation.
- Staff dashboard for tickets, internal notes, escalation review, and refund decisions.
- Audit log records for sensitive actions.
- PostgreSQL persistence with SQLAlchemy and Alembic migration files.
- React + TypeScript frontend and FastAPI backend.

## Technology

| Layer | Implementation |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Axios, Zustand |
| API | Python 3.12+, FastAPI, Pydantic, SQLAlchemy |
| Authentication | JWT bearer tokens; bcrypt password hashing |
| Database | PostgreSQL 16; SQLite is used by the automated test configuration |
| AI | Provider abstraction: MockProvider (default) and GeminiProvider (optional) |
| Retrieval | TF-IDF policy retrieval from `backend/policies/return_policy.md` |
| Migrations | Alembic |
| Tests | pytest |
| Local orchestration | Docker Compose |

## Prerequisites

- Docker Engine and Docker Compose plugin (recommended), or:
  - Python 3.12+
  - Node.js 20+
  - npm
  - PostgreSQL 16+

## Quick start with Docker Compose

Run these commands from the repository root.

```bash
git clone https://github.com/ASEEMNIHAL1/AI-Powered-E-commerce-Customer-Support-Platform.git
cd AI-Powered-E-commerce-Customer-Support-Platform
cp .env.example .env
```

Edit `.env` before starting. At minimum, use a unique random `SECRET_KEY` and a non-default database password. Keep the file local; it is ignored by Git.

```bash
docker compose up --build -d
docker compose ps
docker compose exec backend python seed.py
```

Open:

- Customer and staff frontend: http://localhost:5173
- FastAPI interactive API documentation: http://localhost:8000/docs
- API health check: http://localhost:8000/health

Stop services:

```bash
docker compose down
```

Remove containers and the local database volume (destructive; erases seeded and created database data):

```bash
docker compose down -v
```

### Database initialization and migrations

The FastAPI lifespan currently calls SQLAlchemy `Base.metadata.create_all()` for non-test application startup. The repository also includes two Alembic revisions under `backend/alembic/versions/` for versioned schema management.

To explicitly apply migrations from the backend container:

```bash
docker compose exec backend alembic upgrade head
```

For a local backend environment, run the same command from `backend/` after setting `DATABASE_URL`.

### Seed data

Seed the database after the backend and database are available:

```bash
docker compose exec backend python seed.py
```

The seed script creates two customer accounts, one staff account, one admin account, and ten sample orders. It is idempotent at the user-table level: when any user already exists, it skips the seed operation.

**Demo credentials (local demo only):**

| Role | Email | Password |
|---|---|---|
| Customer | alice@example.com | password123 |
| Customer | bob@example.com | password123 |
| Staff | staff@shopeasy.com | staffpass123 |
| Admin | admin@shopeasy.com | adminpass123 |

Do not reuse these passwords outside the local demonstration.

## Local development without Docker

### 1. Configure the database and environment

Create a PostgreSQL database and user, then copy the template:

```bash
cp .env.example .env
```

Set `DATABASE_URL` to a connection string reachable from your host. The Docker Compose service overrides the backend container's URL to use the Compose database hostname `db`.

### 2. Start the backend

From the repository root:

**Windows PowerShell**
```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**macOS / Linux**
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start the frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Vite serves the frontend at http://localhost:5173. The frontend API base URL is configured with `VITE_API_BASE_URL` in the Docker Compose configuration; for local Vite development, use the API base URL expected by `frontend/src/services/api.ts`.

## Environment variables

Copy `.env.example` to `.env`. Values below are placeholders/defaults for local development only.

| Variable | Purpose |
|---|---|
| `POSTGRES_DB` | PostgreSQL database name used by Docker Compose |
| `POSTGRES_USER` | PostgreSQL username used by Docker Compose |
| `POSTGRES_PASSWORD` | Local PostgreSQL password; replace before use |
| `DATABASE_URL` | SQLAlchemy database connection URL |
| `SECRET_KEY` | JWT signing secret; generate a long random value |
| `ALGORITHM` | JWT signing algorithm (configured as HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry duration |
| `AI_MOCK_MODE` | `true` selects deterministic mock responses; `false` enables configured Gemini mode |
| `GEMINI_API_KEY` | Gemini credential, needed only for live Gemini mode |
| `CORS_ORIGINS` | Comma-separated allowed browser origins |
| `REFUND_ESCALATION_THRESHOLD` | Server-side refund escalation threshold in paise (default 500000 = ₹5,000) |

Never commit `.env`, real API keys, signing secrets, or production credentials. The committed `.env.example` must contain placeholders only.

## Automated tests

The backend test suite is in `backend/tests/`. It covers authentication and customer isolation, refund rules and escalation boundaries, security/failure behavior, and ticket/message flows.

**Windows PowerShell**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:AI_MOCK_MODE = "true"
pytest tests/ -v --tb=short
```

**macOS / Linux**
```bash
cd backend
source .venv/bin/activate
AI_MOCK_MODE=true pytest tests/ -v --tb=short
```

The test fixtures configure an isolated SQLite database and set the testing guard so tests do not use the development PostgreSQL database. The recorded run in `PROJECT_PROGRESS.md` and `FINAL_REQUIREMENTS_AUDIT.md` reports 29 passing tests; rerun the command above in your environment to verify the current checkout.

Frontend production build:

```bash
cd frontend
npm ci
npm run build
```

## API documentation

When the backend is running, use Swagger UI at http://localhost:8000/docs or the OpenAPI JSON at http://localhost:8000/openapi.json.

A human-readable endpoint inventory and example request bodies are in [docs/api.md](docs/api.md). The OpenAPI schema is generated by FastAPI at runtime; no separately exported Postman collection is currently maintained.

## Architecture and data model

- [System architecture and customer-to-human-review flow](docs/architecture.md)
- [Database entities and ER diagram](docs/database-schema.md)

## Customer and support journey

1. Log in as Bob or Alice and inspect the seeded orders.
2. Create a support ticket linked to an order.
3. Open the ticket and send a message to the AI assistant.
4. Ask a return-policy question; the agent can retrieve information from the local return-policy document.
5. Request a refund for an eligible order.
6. A refund above the configured server-side threshold is escalated instead of being automatically approved.
7. Log in as staff and open the escalation queue.
8. Review the case and approve, reject, or request more information.
9. Inspect ticket notes and audit records where exposed by the application.

The application simulates refund workflow state. It does not integrate with a payment gateway or execute a financial transfer.

## Security notes and limitations

- Protected APIs use JWT bearer authentication and role checks.
- Customer-facing order and ticket lookups enforce ownership in backend services.
- Refund validation and escalation thresholds are enforced by backend code, not trusted from browser input.
- Refund idempotency prevents duplicate refund records for the same derived key.
- The Gemini provider is optional and the recorded verification was performed in mock mode; live Gemini behavior requires a valid key and separate verification.
- Use HTTPS, managed secrets, production database hardening, rate limiting, monitoring, and production-grade operational controls before deployment.
- This is an assignment/demo application, not a production payment or customer-data system.

## Repository notes

See [FINAL_REQUIREMENTS_AUDIT.md](FINAL_REQUIREMENTS_AUDIT.md), [SUBMISSION_READINESS_REPORT.md](SUBMISSION_READINESS_REPORT.md), and [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md) for the implementation verification record and remaining demo-video task.
