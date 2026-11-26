# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                         │
│  ┌─────────────────────┐  ┌─────────────────────────┐   │
│  │  Customer Portal    │  │  Support Dashboard      │   │
│  │  (React + TS Vite)  │  │  (React + TS Vite)      │   │
│  │  Port :5173         │  │  Port :5173 /support/*  │   │
│  └──────────┬──────────┘  └──────────┬──────────────┘   │
└─────────────┼──────────────────────-─┼─────────────────┘
              │   HTTPS REST + JWT     │
┌─────────────▼──────────────────────-▼─────────────────┐
│                   FastAPI Backend                       │
│                   Port :8000                            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Auth Middleware (JWT verify)          │   │
│  └─────────────────────┬───────────────────────────┘   │
│                         │                               │
│  ┌─────────────────────▼───────────────────────────┐   │
│  │            RBAC Guards                           │   │
│  │  (get_current_user / get_current_staff)          │   │
│  └──────────┬────────────────────────┬─────────────┘   │
│             │                        │                  │
│  ┌──────────▼─────────┐  ┌───────────▼──────────────┐  │
│  │  Customer Routes   │  │  Support/Admin Routes    │  │
│  │  /auth /orders     │  │  /support/tickets        │  │
│  │  /tickets /refunds │  │  /support/escalations    │  │
│  └──────────┬─────────┘  └───────────┬──────────────┘  │
│             │                        │                  │
│  ┌──────────▼────────────────────────▼──────────────┐   │
│  │            Application Services Layer             │   │
│  │  auth_service  order_service  ticket_service      │   │
│  │  refund_service  escalation_service  audit        │   │
│  │                                                   │   │
│  │  ┌───────────────────────────────────────────┐   │   │
│  │  │         AI Agent (support_agent.py)       │   │   │
│  │  │  ┌─────────────────────────────────────┐  │   │   │
│  │  │  │  AIProvider interface               │  │   │   │
│  │  │  │  MockProvider | GeminiProvider      │  │   │   │
│  │  │  └─────────────────────────────────────┘  │   │   │
│  │  │  Tool Router (backend-enforced):           │   │   │
│  │  │  get_order_details → order_service        │   │   │
│  │  │  search_return_policy → TF-IDF RAG        │   │   │
│  │  │  process_refund → refund_service          │   │   │
│  │  │  escalate_to_human → escalation_service   │   │   │
│  │  └───────────────────────────────────────────┘   │   │
│  └──────────┬────────────────────────────────────────┘  │
└─────────────┼──────────────────────────────────────────┘
              │
┌─────────────▼──────────────────────────────────────────┐
│                   Data Layer                            │
│  ┌────────────────────┐  ┌─────────────────────────┐   │
│  │  PostgreSQL 16     │  │  Local Policy File       │   │
│  │  (SQLAlchemy ORM)  │  │  return_policy.md        │   │
│  │                    │  │  (TF-IDF indexed)        │   │
│  │  - users           │  └─────────────────────────┘   │
│  │  - orders          │                                 │
│  │  - tickets         │  ┌─────────────────────────┐   │
│  │  - messages        │  │  Audit Log Table         │   │
│  │  - refunds         │  │  (all sensitive events)  │   │
│  │  - escalations     │  └─────────────────────────┘   │
│  │  - notes           │                                 │
│  │  - audit_logs      │                                 │
│  └────────────────────┘                                 │
└─────────────────────────────────────────────────────────┘
```

## Refund Request Flow

```
Customer sends "I want a refund" in chat
        │
        ▼
Backend authenticates customer (JWT)
        │
        ▼
AI Agent: identifies intent, checks for order ID
        │
   Missing order ID? ──YES──▶ Ask customer for order ID
        │ NO
        ▼
AI calls: get_order_details(order_id)
   Backend: ownership check ──FAIL──▶ 404 error
        │ PASS
        ▼
AI calls: search_return_policy(category)
   RAG: TF-IDF search over return_policy.md
        │
        ▼
AI calls: process_refund(order_id, amount, reason)
        │
        ▼
Backend refund_service validates:
  1. Customer owns order
  2. Order is delivered
  3. Return window not expired
  4. Amount ≤ order total
  5. No existing active refund
  6. Idempotency key check
        │
   Amount > ₹5000?
   YES ──▶ Create ESCALATED refund + Escalation record
              │
              ▼
         Staff reviews in dashboard
         Approve/Reject/More Info
   NO ──▶ Create PENDING refund record
        │
        ▼
Persist messages, audit events
Return result to customer
```

## Security Layers

1. **Transport**: HTTPS in production
2. **Authentication**: JWT Bearer token on every protected route
3. **Authorization**: Role guards (`get_current_active_customer`, `get_current_staff`)
4. **Object ownership**: All DB queries include `WHERE customer_id = auth_user.id`
5. **Input validation**: Pydantic schemas on all request bodies
6. **SQL injection**: SQLAlchemy ORM with parameterized queries
7. **Prompt injection**: 
   - System prompt never mixed with user content
   - Customer identity from JWT, not from LLM-generated args
   - Business rules enforced server-side regardless of LLM output
8. **Audit trail**: All sensitive events logged to `audit_logs`
