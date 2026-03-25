import json
import time
from pathlib import Path

from app import app

DATASET_PATH = Path("evaluation_samples.json")


def load_cases():
    if not DATASET_PATH.exists():
        return []
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def run():
    client = app.test_client()
    results = []

    health = client.get("/api/health")
    status = client.get("/api/status")
    results.append({"check": "health_endpoint", "passed": health.status_code == 200})
    results.append({"check": "status_endpoint", "passed": status.status_code == 200})

    for case in load_cases():
        started = time.time()
        response = client.post("/api/chat", json={"message": case["message"], "history": []})
        elapsed_ms = round((time.time() - started) * 1000, 2)
        payload = response.get_json() or {}
        text = payload.get("response", "")
        passed = response.status_code == 200 and any(term.lower() in text.lower() for term in case["expected_terms"])
        results.append(
            {
                "check": case["name"],
                "passed": passed,
                "latency_ms": elapsed_ms,
                "request_id": payload.get("request_id"),
            }
        )

    summary = {
        "total": len(results),
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "results": results,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
