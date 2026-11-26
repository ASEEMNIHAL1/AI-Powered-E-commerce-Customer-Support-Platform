# PROJECT_PROGRESS.md

## Session: 2026-11-25 (Resumed & Verified)

### Phase 0: Inspect & Plan — VERIFIED
- Inspected existing repository structure, `DECISIONS.md`, and all backend/frontend files.

### Phase 1: Foundation — VERIFIED
- `docker-compose.yml`, `.env.example`, `.env`, `.gitignore`, `backend/Dockerfile`, `frontend/Dockerfile`, `backend/requirements.txt`.
- All 3 Docker Compose services (`acs_db`, `acs_backend`, `acs_frontend`) built and started cleanly.

### Phase 2: Database Models & Migrations — VERIFIED
- Added missing `AuditLog, AuditEventType` import to `backend/app/models/__init__.py`.
- Generated Alembic migrations:
  - `634a91af776e_initial_schema.py` (with PostgreSQL enum cleanup in `downgrade()`)
  - `2f0a750f74b5_add_audit_logs.py`
- Tested `alembic upgrade head`, `alembic downgrade base`, `alembic upgrade head` against PostgreSQL 16 (`acs_db`).
- Seeded demo data via `python seed.py` (4 users, 10 orders).

### Phase 3: Auth & RBAC — VERIFIED
- Fixed `passlib` + `bcrypt>=4.1` incompatibility in `backend/app/core/security.py` by using `bcrypt` directly.
- Verified `/auth/register`, `/auth/login`, `/auth/me`, and role-based access control (`403` for customer on `/support/tickets`).

### Phase 4: Core Backend APIs — VERIFIED
- Verified `/orders`, `/tickets`, `/tickets/{id}/messages`, `/tickets/{id}/chat`, `/refunds`, `/support/tickets`, `/support/escalations`, `/support/escalations/{id}/decision`.

### Phase 5: Frontend (Customer + Staff) — VERIFIED
- Fixed token race condition in `frontend/src/stores/authStore.ts` (`setToken`) and `frontend/src/pages/auth/LoginPage.tsx` (sets token before calling `/auth/me`).
- Added `frontend/src/vite-env.d.ts` for `import.meta.env` types.
- Installed dependencies (`npm install`: 166 packages).
- Ran `npm run build` (`tsc && vite build`): **0 errors**, built in 1.44s.

### Phase 6: AI Agent & Tools — VERIFIED
- Verified `MockProvider` deterministic chat and missing-order-ID clarification flow in both `pytest` and live Docker Compose runtime.
- `search_return_policy` TF-IDF retriever over `backend/policies/return_policy.md`.

### Phase 7: Security & Business Rules — VERIFIED
- Idempotency (`idempotency_key` UNIQUE constraint), ₹5,000 threshold enforcement, prompt injection resistance, IDOR prevention (`404` on other customer's resources), and `audit_logs` persistence verified.

### Phase 8: Automated Tests — VERIFIED
- Fixed `backend/main.py` lifespan (`TESTING=true` guard) and `backend/tests/conftest.py` so `pytest` uses SQLite (`sqlite:///./test.db`) and never touches PostgreSQL.
- Ran `pytest tests/ -v --tb=short`: **29 passed, 0 failed, 0 errors** in 10.61s.

### Phase 9: Docs & Runtime Verification — VERIFIED
- `GET http://localhost:8000/health` → `{"status":"ok"}`
- `GET http://localhost:5173` → `HTTP 200`
- End-to-end runtime flow verified: Alice login → `/auth/me` → RBAC 403 on `/support/tickets` → 6 orders → ticket creation → AI chat clarification → high-value refund (>₹5,000) auto-escalated → Staff login → escalation queue → escalation approved.

---

## Remaining Limitations / Notes
- `AI_MOCK_MODE=true` is used for local/test runs; live Gemini mode requires setting `AI_MOCK_MODE=false` and a valid `GEMINI_API_KEY` in `.env`.
- `docker-compose.yml` has a harmless `version: "3.9"` deprecation warning from Docker Compose v5.

---

## Final Requirements Audit: 2026-11-26 — VERIFIED
- Executed all 10 mandatory scenarios + 3 additional checks against the live Docker Compose stack (`http://localhost:8000`).
- All 10 scenarios and 3 additional checks **PASSED**.
- Created `FINAL_REQUIREMENTS_AUDIT.md` with full requirement-by-requirement evidence.
