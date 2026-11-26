# Architecture Decisions (DECISIONS.md)

## Technology Choices

| Decision | Choice | Reason |
|----------|--------|--------|
| LLM Provider | Gemini 1.5 Flash (optional) + Mock mode | Free tier available; mock mode enables zero-cost tests |
| Password hashing | bcrypt (passlib) | Industry standard; Argon2 available as upgrade |
| JWT | python-jose HS256 | Simple, well-tested, 60-min expiry |
| ORM | SQLAlchemy 2.0 | Type-safe mapped_column API |
| Policy retrieval | TF-IDF (scikit-learn) | No paid vector DB needed; inspectable and local |
| Idempotency | SHA-256(order_id + customer_id + amount_paise) | Deterministic, collision-resistant, server-side |
| Money storage | Integer paise (₹1 = 100 paise) | Avoids floating-point rounding errors |
| Test DB | SQLite (in-memory) | No PostgreSQL needed for tests |

## Business Rule Implementations

### Refund Threshold (₹5,000)
- Stored as `REFUND_ESCALATION_THRESHOLD = 500000` paise in `Settings`
- Read from env var, never from frontend or LLM output
- Enforced in `refund_service.process_refund()` — not in the AI agent

### Return Windows
```python
RETURN_WINDOW_DAYS = {
    ItemCategory.ELECTRONICS: 30,
    ItemCategory.FOOD: 7,
    ItemCategory.CLOTHING: 15,
    ItemCategory.BOOKS: 15,
    ItemCategory.HOME: 15,
    ItemCategory.OTHER: 15,
}
```

### Prompt Injection Resistance
1. **System prompt separation**: System instructions are never mixed with user messages
2. **Tool args ignored for identity**: `customer` identity always comes from JWT, never from tool args
3. **Backend validation**: Even if LLM calls `process_refund(order_id=X)`, backend enforces ownership
4. **Reason field sanitized**: Injection text in reason field cannot change refund logic

### IDOR Prevention
- All customer queries include `WHERE customer_id = current_user.id`
- Returning 404 (not 403) on unauthorized object access to avoid confirming existence

## Deviations from Assignment

1. **Alembic migrations**: Included but `create_all` used for local dev simplicity; Alembic is fully configured for production use
2. **Vector DB**: Assignment allows keyword retrieval; TF-IDF chosen for zero-dependency local RAG
3. **Return window**: Assignment didn't specify durations; documented sample policies created
4. **Multi-turn tool calling**: Single-step tool execution (one tool per turn); can be extended to multi-step
