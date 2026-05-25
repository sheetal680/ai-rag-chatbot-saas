.PHONY: venv install run dev test test-unit test-integration lint typecheck clean

# ── Environment ───────────────────────────────────────────────────────────────

venv:
	python -m venv .venv
	@echo "Activate with:  .venv\\Scripts\\activate  (Windows)"
	@echo "             or source .venv/bin/activate  (Unix)"

install:
	pip install -r requirements.txt

# ── Dev server ────────────────────────────────────────────────────────────────

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn main:app --reload --port 8000

# ── Tests ─────────────────────────────────────────────────────────────────────

test:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-all:
	pytest -v

# ── Code quality ──────────────────────────────────────────────────────────────

lint:
	ruff check .

typecheck:
	mypy app main.py

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true
