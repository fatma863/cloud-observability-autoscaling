import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "app"))

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_fast_endpoint():
    response = client.get("/api/v1/workload/fast")
    assert response.status_code == 200
    assert "latency_ms" in response.json()

def test_compute_endpoint():
    response = client.get("/api/v1/workload/compute?intensity=3")
    assert response.status_code in [200, 500]

def test_prometheus_metrics_export():
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    # Verify our custom Prometheus metrics are present in exposition format
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "system_simulated_cpu_utilization_ratio" in body

