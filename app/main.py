from fastapi import FastAPI, Response, status, Query
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random
import os

app = FastAPI(
    title="Cloud Observability Instrumented Service",
    description="Microservice with real-time Prometheus telemetry, custom metrics, and traffic simulations",
    version="1.0.0"
)

# Prometheus Metrics Definitions
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the service",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

ACTIVE_CONNECTIONS = Gauge(
    "http_active_connections",
    "Number of current active incoming HTTP requests"
)

SIMULATED_CPU_LOAD = Gauge(
    "system_simulated_cpu_utilization_ratio",
    "Simulated CPU utilization ratio between 0.0 and 1.0"
)

@app.get("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz", status_code=status.HTTP_200_OK)
def health():
    return {"status": "healthy", "service": "observability-target"}

@app.get("/api/v1/workload/fast")
def fast_endpoint():
    ACTIVE_CONNECTIONS.inc()
    start_time = time.time()
    try:
        # Fast endpoint: 10-30ms
        latency = random.uniform(0.01, 0.03)
        time.sleep(latency)
        status_code = "200"
        REQUEST_COUNT.labels(method="GET", endpoint="/fast", status_code=status_code).inc()
        REQUEST_LATENCY.labels(endpoint="/fast").observe(time.time() - start_time)
        return {"status": "ok", "latency_ms": round(latency * 1000, 2)}
    finally:
        ACTIVE_CONNECTIONS.dec()

@app.get("/api/v1/workload/compute")
def compute_heavy_endpoint(intensity: int = Query(5, ge=1, le=10)):
    ACTIVE_CONNECTIONS.inc()
    start_time = time.time()
    try:
        # Simulate compute-intensive operation
        simulated_load = min(1.0, intensity * 0.1)
        SIMULATED_CPU_LOAD.set(simulated_load)
        
        # Simulate variable processing latency
        sleep_dur = intensity * 0.05 + random.uniform(0.02, 0.1)
        time.sleep(sleep_dur)

        # 5% chance of simulated error to trigger Prometheus alerting
        if random.random() < 0.05:
            REQUEST_COUNT.labels(method="GET", endpoint="/compute", status_code="500").inc()
            return Response(content='{"error": "Simulated upstream failure"}', status_code=500, media_type="application/json")

        status_code = "200"
        REQUEST_COUNT.labels(method="GET", endpoint="/compute", status_code=status_code).inc()
        REQUEST_LATENCY.labels(endpoint="/compute").observe(time.time() - start_time)
        return {"status": "computed", "intensity": intensity, "latency_ms": round((time.time() - start_time) * 1000, 2)}
    finally:
        ACTIVE_CONNECTIONS.dec()

