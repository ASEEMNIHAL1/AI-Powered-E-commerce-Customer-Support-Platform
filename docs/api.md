# API Reference

This reference is based on the FastAPI routers and Pydantic schemas in `backend/app/api/` and `backend/app/schemas/`. The runtime OpenAPI schema is authoritative for the current checkout.

## Base URL and authentication

Local API base URL: `http://localhost:8000`

All protected endpoints expect a bearer token returned by `POST /auth/login`.

```http
Authorization: Bearer <access_token>
```

Interactive docs: `http://localhost:8000/docs`  
OpenAPI JSON: `http://localhost:8000/openapi.json`

## Authentication endpoints

| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Register customer |
| POST | `/auth/login` | Public | Authenticate and return a JWT |
| GET | `/auth/me` | Authenticated | Return current user's profile |

Register body:

```json
{
  "name": "Bob Sharma",
  "email": "bob@example.com",
  "password": "password123"
}
```

Login body:

```json
{
  "email": "bob@example.com",
  "password": "password123"
}
```

The registration schema requires a non-empty name and password of at least 8 characters. Email is validated as an email address.

## Customer endpoints

| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/orders` | Customer | List orders belonging to the current customer |
| GET | `/orders/{order_id}` | Customer | Retrieve one owned order |
| POST | `/tickets` | Customer | Create a support ticket |
| GET | `/tickets` | Customer | List the current customer's tickets |
| GET | `/tickets/{ticket_id}` | Customer | Retrieve one owned ticket |
| PATCH | `/tickets/{ticket_id}` | Authenticated | Update ticket through the ticket service |
| GET | `/tickets/{ticket_id}/messages` | Customer | Retrieve persisted ticket messages |
| POST | `/tickets/{ticket_id}/chat` | Customer | Send a message to the AI agent |
| POST | `/refunds` | Customer | Create a refund request |
| GET | `/refunds` | Customer | List own refund records |
| GET | `/refunds/{refund_id}` | Customer | Retrieve one owned refund record |

Ticket creation body:

```json
{
  "subject": "Help with my order",
  "description": "The item arrived with an issue.",
  "category": "product",
  "order_id": 2,
  "priority": "medium"
}
```

Ticket category values: `refund`, `shipping`, `product`, `payment`, `account`, `other`. Priority values: `low`, `medium`, `high`, `urgent`. The `order_id` is optional and priority defaults to `medium`.

Chat body:

```json
{
  "content": "Can you explain the return policy for this order?"
}
```

Refund creation body:

```json
{
  "order_id": 2,
  "ticket_id": 1,
  "amount_paise": 100000,
  "reason": "The item arrived damaged."
}
```

The refund amount must be a positive integer in paise (100 paise = ₹1), and the reason must not be empty. The backend performs ownership, order-state, return-window, amount, duplicate, and escalation checks.

## Staff and admin endpoints

| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/support/tickets` | Staff/admin | List tickets; optional `status` and `priority` query filters |
| GET | `/support/tickets/{ticket_id}` | Staff/admin | Retrieve ticket details |
| PATCH | `/support/tickets/{ticket_id}` | Staff/admin | Update ticket status/priority |
| GET | `/support/escalations` | Staff/admin | List the escalation queue |
| POST | `/support/escalations/{escalation_id}/decision` | Staff/admin | Record a human review decision |
| POST | `/support/tickets/{ticket_id}/notes` | Staff/admin | Add an internal note |
| GET | `/support/tickets/{ticket_id}/notes` | Staff/admin | List internal notes |

Escalation decision body:

```json
{
  "decision": "approved",
  "note": "Reviewed the order and supporting details.",
  "refund_decision": "approve"
}
```

The `decision` field uses the `EscalationStatus` enum. The optional `refund_decision` is passed through to the decision service (documented in code as `approve` or `reject`). Consult the live Swagger schema for accepted values and any application-level constraints.

Internal notes are staff-only and are not customer conversation messages.

## Health endpoint

| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/health` | Public | Returns `{"status":"ok"}` while the API process is healthy |

## Common HTTP responses

- `401 Unauthorized`: token is missing or invalid.
- `403 Forbidden`: authenticated user does not have the required role.
- `404 Not Found`: resource does not exist or is not visible to the requesting customer.
- `422 Unprocessable Entity`: request validation or business-rule rejection.

## Exporting a Postman collection

A static Postman export is not committed because FastAPI builds the OpenAPI document from the source code. With the backend running:

1. Open Postman.
2. Select **Import**.
3. Choose **Link** and enter `http://localhost:8000/openapi.json`, or save the document with:

```bash
curl http://localhost:8000/openapi.json -o openapi.json
```

4. Import the saved JSON file into Postman.

Re-export after API changes so the collection matches the current schemas.
