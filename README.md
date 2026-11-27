# AI-Powered E-commerce Customer Support Platform

> A full-stack application for e-commerce customer support with AI agent, refund management, and escalation workflows.
### DEMO VIDEO:https://drive.google.com/file/d/1WV41QFa2Q1fRmlwyA5dWoPnkAueFXQlU/view?usp=sharing

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+ (or Docker)
- Docker & Docker Compose (for containerized run)

### Option A: Docker Compose (Recommended)

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env: set SECRET_KEY, POSTGRES_PASSWORD

# 2. Start all services
docker compose up --build

# 3. Seed demo data
docker compose exec backend python seed.py

# 4. Access
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

### Option B: Local Development

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
cp ../.env.example ../.env    # Edit .env

# Start PostgreSQL, then:
alembic upgrade head
python seed.py
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 🔑 Demo Credentials (after seeding)

| Role     | Email                     | Password      |
|----------|---------------------------|---------------|
| Customer | alice@example.com         | password123   |
| Customer | bob@example.com           | password123   |
| Staff    | staff@shopeasy.com        | staffpass123  |
| Admin    | admin@shopeasy.com        | adminpass123  |

## 🧪 Running Tests

```bash
cd backend
.venv\Scripts\activate

# Install test deps (included in requirements.txt)
# AI_MOCK_MODE=true is set by default for tests (no API key needed)
AI_MOCK_MODE=true pytest tests/ -v
```

## 📁 Environment Variables

See [`.env.example`](.env.example) for all variables. Key ones:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | sqlite in tests |
| `SECRET_KEY` | JWT signing key (change in production!) | — |
| `AI_MOCK_MODE` | Use mock AI (no API key needed) | `true` |
| `GEMINI_API_KEY` | Gemini API key (only if `AI_MOCK_MODE=false`) | — |
| `REFUND_ESCALATION_THRESHOLD` | Escalation threshold in paise | `500000` (₹5000) |

## 🏗 Architecture

```
React (Vite + TypeScript + Tailwind)
        |
        v
FastAPI REST API (Python 3.12)
        |
   Auth/RBAC Layer
        |
  Application Services
   /    |    \    \
  v     v     v    v
PostgreSQL  AI Agent  Audit Log  Policy RAG
(SQLAlchemy)   |
           Tool Router
           /   |   \
          v    v    v
       Order  Policy  Refund/
       Lookup Search  Escalation
                     |
              Backend Validation
              (₹5000 threshold,
               idempotency,
               ownership check)
```

## 📖 API Documentation

Swagger UI available at **http://localhost:8000/docs** when running.

Key endpoints:
- `POST /auth/register` – Register new customer
- `POST /auth/login` – Login and get JWT
- `GET /orders` – Customer's orders
- `POST /tickets` – Create support ticket
- `POST /tickets/{id}/chat` – Chat with AI agent
- `POST /refunds` – Request refund
- `GET /support/escalations` – Staff escalation queue

## 🔒 Security Design

1. **Authentication**: JWT (HS256, 60-min expiry)
2. **Password hashing**: bcrypt via passlib
3. **Authorization**: Role-based (customer/staff/admin), enforced per route
4. **IDOR prevention**: All queries filtered by authenticated user ID
5. **Prompt injection resistance**: System prompt isolation + backend-enforced rules
6. **Idempotency**: SHA-256 key prevents duplicate refund records
7. **Refund threshold**: Enforced server-side — ₹5000 threshold never read from client
8. **Audit logging**: All refund/escalation events logged to `audit_logs` table

## 🤖 AI Agent

- **Mock mode** (default): Deterministic responses for testing without API keys
- **Gemini mode**: Set `AI_MOCK_MODE=false` and `GEMINI_API_KEY=your_key`
- Provider interface at `backend/app/agents/support_agent.py`
- Policy retrieval: TF-IDF keyword search over `backend/policies/return_policy.md`

## 📊 Database Schema

See [`docs/database-schema.md`](docs/database-schema.md)

## 🏛 Architecture Diagram

See [`docs/architecture.md`](docs/architecture.md)

## 🎥 Demo Walkthrough (5–7 minutes)

1. **Customer journey**: Register → Login → View Orders → Create Ticket → Chat with AI → Request Refund
2. **Escalation flow**: Request high-value refund → AI creates escalation → Log in as staff → Review queue → Approve/Reject
3. **Security demo**: Try accessing another user's order → see 404; Inject text in reason → escalation still triggers
4. **Policy retrieval**: Ask about return window in chat → AI retrieves and cites local policy doc
