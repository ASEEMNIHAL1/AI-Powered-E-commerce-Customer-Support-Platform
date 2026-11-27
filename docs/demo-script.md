# Demo Walkthrough Script (5–10 minutes)

## Before recording

1. Start the project from the repository root: `docker compose up --build -d`.
2. On a fresh database, seed the demo data: `docker compose exec backend python seed.py`.
3. Open the frontend at http://localhost:5173 and keep http://localhost:8000/docs available.
4. Prepare a second browser window for staff login.
5. Keep `AI_MOCK_MODE=true` for deterministic responses. Do not show the contents of the real `.env` file.
6. Confirm the demo account works before recording.

The seed script provides Alice and Bob as customers, plus staff and admin accounts. Suggested customer: `bob@example.com` / `password123`. Staff: `staff@shopeasy.com` / `staffpass123`.

## Timeline and spoken script

### 0:00–0:45 — Introduction

**Say:** “This is an AI-powered e-commerce customer-support platform. It gives customers a place to view orders, create support tickets, ask questions, and request refunds. Support staff have a separate dashboard to handle tickets and review escalated cases. The AI assists with routine support, while sensitive decisions are validated by backend business rules and can require human review.”

Show the login page and identify the customer and staff experiences.

### 0:45–1:30 — Customer login and orders

Log in as Bob and open the orders page.

**Say:** “I am logging in as Bob, one of the seeded demo customers. The backend verifies his credentials and returns a JWT. The frontend attaches that token to protected API requests. The order list is scoped to the authenticated customer, so Bob sees his own orders.”

Open one of Bob's orders and show its status and details.

### 1:30–2:30 — Create support ticket

Create a ticket and associate it with an order.

**Say:** “When Bob needs help, he creates a support ticket and can link it to the relevant order. The ticket is stored in the database and linked to Bob's user record. On later requests, the backend checks ownership rather than trusting an order or ticket ID supplied by the browser.”

### 2:30–3:45 — AI conversation and policy retrieval

Open the ticket conversation and ask a question about returns.

**Say:** “The customer message is sent to the ticket chat endpoint. The support agent uses a provider interface. For this demo, mock mode gives deterministic responses without requiring an external API key. The policy retrieval tool searches the local return-policy document using TF-IDF. Both customer and agent messages are persisted.”

Show the message history.

### 3:45–5:00 — Refund rules and escalation

Request a refund for an eligible order. Then show a high-value refund case using an amount above ₹5,000, subject to the order and ticket data and validations available in the running demo.

**Say:** “The AI does not have authority to approve a refund by itself. The refund service checks the authenticated customer owns the order, the order is eligible, the return window is valid, the requested amount does not exceed the order amount, and duplicate requests are handled through an idempotency key. A request above the configured ₹5,000 threshold becomes an escalation instead of being automatically approved.”

**Important narration:** “This is a simulated refund workflow. It creates database records and does not transfer money or call a payment gateway.”

### 5:00–6:30 — Human review in the support dashboard

Log out and sign in as staff. Open the staff dashboard and escalation queue.

**Say:** “Staff accounts have access to a separate, role-protected support dashboard. They can inspect the escalated case and record a decision. The backend records the decision and relevant audit information. This is the human-in-the-loop step: AI can assist with the request, but a staff member reviews a sensitive case.”

Open the escalation detail and show the available decision controls. Use only a demo record for any action.

### 6:30–7:30 — Security and API documentation

Show the API docs or the project’s security documentation.

**Say:** “The backend uses JWT authentication, role-based authorization, customer ownership checks, Pydantic input validation, server-side refund rules, idempotency, and audit records. A customer should not be able to access staff-only endpoints or another customer's order.”

Optionally demonstrate a customer receiving a forbidden response from a staff-only route, using Swagger's Authorize feature with the customer's token.

### 7:30–8:00 — Closing

**Say:** “The project combines a full-stack customer support experience, an AI assistant with policy retrieval, deterministic business-rule enforcement, and staff review for escalations. The repository includes setup instructions, environment configuration, database migrations and seed data, architecture and database diagrams, API documentation, and automated test instructions.”

## Recording checklist

- [ ] Customer login and order list shown.
- [ ] Support ticket created.
- [ ] AI conversation and policy retrieval shown.
- [ ] Refund validation and escalation explained.
- [ ] Staff dashboard and human decision shown.
- [ ] API documentation or security controls shown.
- [ ] No real credentials, tokens, or local `.env` values visible.
- [ ] Explicitly state that refunds are simulated.
- [ ] Keep the final recording between 5 and 10 minutes.
