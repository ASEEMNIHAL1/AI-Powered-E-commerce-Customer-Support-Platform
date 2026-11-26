"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
import app.models  # ensure all models are registered  # noqa: F401
from app.api import auth, orders, tickets, messages, refunds, support


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Skip automatic table creation during pytest; tests manage their own SQLite schema.
    if os.environ.get("TESTING") != "true":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Customer Support Platform",
    description="E-commerce customer support with AI agent, refund management, and escalation workflows.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(tickets.router)
app.include_router(messages.router)
app.include_router(refunds.router)
app.include_router(support.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
