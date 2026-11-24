from locust import HttpUser, task, between
import random

class CloudTrafficSimulator(HttpUser):
    # Wait between 0.1s and 0.5s to generate realistic concurrent web traffic
    wait_time = between(0.1, 0.5)

    @task(5)
    def test_fast_endpoint(self):
        """Simulate frequent lightweight API calls."""
        self.client.get("/api/v1/workload/fast")

    @task(2)
    def test_compute_endpoint(self):
        """Simulate variable compute workloads that trigger CPU load spikes."""
        intensity = random.randint(1, 9)
        self.client.get(f"/api/v1/workload/compute?intensity={intensity}")

    @task(1)
    def test_health_check(self):
        """Standard heartbeat check."""
        self.client.get("/healthz")

