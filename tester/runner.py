"""Execute all tests and compute QoS metrics."""

import statistics
from datetime import datetime, timezone

from tester.tests import ALL_TESTS


def run_all():
    """Run every test and return a structured run result dict."""
    results = []
    latencies = []
    passed = 0
    failed = 0

    for test_fn in ALL_TESTS:
        try:
            name, status, latency_ms, details = test_fn()
        except Exception as exc:
            name = test_fn.__name__
            status = "FAIL"
            latency_ms = 0
            details = str(exc)

        results.append({
            "name": name,
            "status": status,
            "latency_ms": latency_ms,
            "details": details,
        })
        latencies.append(latency_ms)
        if status == "PASS":
            passed += 1
        else:
            failed += 1

    total = passed + failed
    error_rate = round(failed / total, 3) if total else 0
    avg_latency = round(statistics.mean(latencies), 1) if latencies else 0
    p95_latency = round(sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0, 1)

    return {
        "api": "AlQuran Cloud",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "error_rate": error_rate,
            "latency_ms_avg": avg_latency,
            "latency_ms_p95": p95_latency,
            "availability": round(1 - error_rate, 3),
        },
        "tests": results,
    }
