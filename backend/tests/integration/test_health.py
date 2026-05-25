"""Integration test — verifies the health endpoint returns 200.

Run with: pytest tests/integration -v
Requires: backend dependencies installed, no real DB needed for /health.
"""


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
