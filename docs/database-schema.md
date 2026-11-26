# Database Schema (ER Diagram)

## Entity Relationship Overview

```mermaid
erDiagram
    USERS {
        int id PK
        string name
        string email UK
        string hashed_password
        enum role "customer|staff|admin"
        bool is_active
        datetime created_at
    }

    ORDERS {
        int id PK
        int customer_id FK
        enum status "pending|confirmed|shipped|delivered|cancelled|returned"
        string item_name
        enum category "electronics|clothing|food|books|home|other"
        int total_amount_paise
        date delivery_date
        datetime created_at
    }

    TICKETS {
        int id PK
        int customer_id FK
        int order_id FK
        string subject
        text description
        enum category "refund|shipping|product|payment|account|other"
        enum status "open|in_progress|awaiting_customer|escalated|resolved|closed"
        enum priority "low|medium|high|urgent"
        datetime created_at
        datetime updated_at
    }

    MESSAGES {
        int id PK
        int ticket_id FK
        enum sender_type "customer|agent|system"
        int sender_id FK
        text content
        datetime created_at
    }

    REFUNDS {
        int id PK
        int order_id FK
        int ticket_id FK
        int amount_paise
        text reason
        enum status "pending|approved|rejected|escalated|cancelled"
        string idempotency_key UK
        int requested_by FK
        int reviewed_by FK
        text review_note
        datetime created_at
        datetime updated_at
    }

    ESCALATIONS {
        int id PK
        int ticket_id FK
        int refund_id FK
        text summary
        enum priority "low|medium|high|urgent"
        enum status "open|under_review|approved|rejected|more_info_requested|resolved"
        int assigned_to FK
        text decision_note
        datetime created_at
        datetime updated_at
    }

    NOTES {
        int id PK
        int ticket_id FK
        int author_id FK
        text content
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        enum event_type
        int actor_id FK
        string target_type
        int target_id
        text detail
        datetime created_at
    }

    USERS ||--o{ ORDERS : "places"
    USERS ||--o{ TICKETS : "creates"
    ORDERS ||--o{ TICKETS : "referenced_by"
    TICKETS ||--o{ MESSAGES : "contains"
    ORDERS ||--o{ REFUNDS : "has"
    TICKETS ||--o{ REFUNDS : "has"
    TICKETS ||--o{ ESCALATIONS : "has"
    REFUNDS ||--o| ESCALATIONS : "escalated_as"
    TICKETS ||--o{ NOTES : "has"
    USERS ||--o{ AUDIT_LOGS : "generates"
```

## Key Constraints

| Table | Constraint | Purpose |
|-------|-----------|---------|
| `users.email` | UNIQUE | Prevent duplicate accounts |
| `refunds.idempotency_key` | UNIQUE | Prevent duplicate refund processing |
| `orders.customer_id` | FK → users | Ownership link |
| `tickets.customer_id` | FK → users | Ownership link |
| `refunds.requested_by` | FK → users | Audit: who requested |
| `refunds.reviewed_by` | FK → users | Audit: who approved/rejected |
