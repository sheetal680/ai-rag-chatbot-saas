"""Shared pytest fixtures for unit and integration tests."""
import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Provide dummy env vars so pydantic-settings doesn't fail on startup
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("GROQ_API_KEY", "gsk-test-key")
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:test@localhost:5432/test_db")

# Pre-import so patch() can resolve the submodule path without asyncpg installed
import app.db.postgres  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """Synchronous test client with DB lifecycle mocked out."""
    with (
        patch("app.db.postgres.connect_db", new_callable=AsyncMock),
        patch("app.db.postgres.disconnect_db", new_callable=AsyncMock),
        patch("app.db.postgres.ensure_tables", new_callable=AsyncMock),
    ):
        from main import app
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c
