from __future__ import annotations

import json
from typing import Any, List, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "AI RAG Chatbot"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str
    # Accepts JSON array OR comma-separated:
    #   ALLOWED_ORIGINS=https://app.vercel.app,https://yourdomain.com
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── LLM provider ─────────────────────────────────────────────────────────
    # "auto" selects Groq → Gemini → Ollama based on which keys are present.
    LLM_PROVIDER: str = "auto"

    # Groq (primary)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Google Gemini (fallback)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Ollama (local dev)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # ── Embeddings ────────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── PostgreSQL / Supabase ─────────────────────────────────────────────────
    # Leave empty to skip DB on startup (server boots; DB-dependent routes
    # return errors). Required for production.
    DATABASE_URL: str = ""

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "documents"

    # ── Meta / WhatsApp Business API (optional — leave blank to disable) ────────
    # Obtain from Meta for Developers → your App → WhatsApp → API Setup
    META_WEBHOOK_VERIFY_TOKEN: str = ""  # a secret string you choose; set in Meta dashboard
    META_APP_SECRET: str = ""            # App → Settings → Basic → App Secret
    META_WHATSAPP_TOKEN: str = ""        # System user access token
    META_PHONE_NUMBER_ID: str = ""       # Phone Number ID from API Setup page
    META_API_VERSION: str = "v19.0"

    # ── Derived helpers ───────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def docs_url(self) -> str | None:
        return None if self.is_production else "/docs"

    @property
    def redoc_url(self) -> str | None:
        return None if self.is_production else "/redoc"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: Any) -> list[str]:
        """Accept a JSON array string or a comma-separated string."""
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return v


settings = Settings()
