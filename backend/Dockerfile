FROM python:3.11-slim

# System deps for PyMuPDF, lxml, and health-check curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    libfreetype6-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install CPU-only torch BEFORE requirements.txt so pip doesn't pull the
# CUDA variant (~700 MB extra) when it resolves sentence-transformers deps.
RUN pip install --no-cache-dir \
    torch==2.4.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python deps — cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model into the image so there's no cold-start
# network fetch on the first request.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application source
COPY . .

# Non-root user for security
RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/chroma_data \
    && chown -R appuser:appuser /app

USER appuser

# Railway / Render inject PORT at runtime; 8000 is the local default
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Liveness probe — Railway and Render poll /health
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 2 uvicorn workers — scales with CPU on the smallest Railway/Render instances.
# Increase to 4 on plans with 2+ vCPUs.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 2 --log-level info"]
