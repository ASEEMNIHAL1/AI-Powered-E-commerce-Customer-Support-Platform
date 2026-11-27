# Submission Checklist

Use this checklist for final hand-off. A documentation file being present does not replace the need to run the app and record the requested walkthrough.

| Requirement | Repository location / evidence | Status |
|---|---|---|
| Source code | `backend/`, `frontend/`, `docker-compose.yml` | Present |
| README with prerequisites and setup | `README.md` | Updated on documentation branch |
| Environment variable guide | `.env.example`, `README.md` | Present |
| Database setup and migrations | `backend/alembic/`, README | Present; app startup also calls metadata table creation outside tests |
| Seed-data instructions | `backend/seed.py`, README | Present |
| Architecture diagram | `docs/architecture.md` | Mermaid component and workflow diagrams |
| Database ER diagram | `docs/database-schema.md` | Mermaid ER diagram |
| API documentation / collection | `docs/api.md`, runtime `/docs` and `/openapi.json` | API docs present; collection can be exported from OpenAPI |
| Automated tests and instructions | `backend/tests/`, README | Present; recorded run reports 29 passing |
| 5–10 minute demo video | Follow `docs/demo-script.md` | **Record and upload video** |
| Secret-safe environment template | `.env.example` | Present; placeholder values only |

## Final manual verification

- [ ] Run the backend test suite from the current checkout.
- [ ] Run `npm ci && npm run build` in `frontend/`.
- [ ] Run `docker compose up --build`; confirm frontend, API docs, and health endpoint.
- [ ] Seed a fresh database and verify the four demo logins.
- [ ] Export the current `/openapi.json` and import it into Postman if the reviewer expects a collection file.
- [ ] Record a 5–10 minute demo using `docs/demo-script.md`.
- [ ] Confirm `.env`, API keys, tokens, database files, local virtual environments, and dependency folders are not tracked.
- [ ] Review the Git diff before merging the documentation branch.

## Scope and verification caveats

- The last recorded automated test run in project documentation reports 29 passed. Rerun tests against the exact final commit before submission.
- Mock AI mode is the reproducible default. Live Gemini mode requires a real API key and has not been verified by the recorded run.
- Refund processing creates application records only; there is no payment gateway integration or money transfer.
- The seed script skips seeding if it detects at least one existing user.
- The current README documents both Alembic migrations and the app's non-test startup call to SQLAlchemy metadata table creation. Keep these behaviors in mind when explaining database initialization.
