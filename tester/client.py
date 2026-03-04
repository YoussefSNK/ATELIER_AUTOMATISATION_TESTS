"""HTTP client wrapper with timeout, retry and latency measurement."""

import time
import requests

BASE_URL = "https://api.alquran.cloud/v1"
TIMEOUT = 5  # seconds
MAX_RETRIES = 1


def get(endpoint, params=None):
    """Send a GET request with timeout, 1 retry, and latency tracking.

    Returns (response, latency_ms) or raises after retries exhausted.
    """
    url = f"{BASE_URL}{endpoint}"
    last_exc = None

    for attempt in range(1 + MAX_RETRIES):
        try:
            start = time.perf_counter()
            resp = requests.get(url, params=params, timeout=TIMEOUT)
            latency_ms = round((time.perf_counter() - start) * 1000, 1)

            # Retry on 429 or 5xx
            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt < MAX_RETRIES:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue
            return resp, latency_ms

        except requests.exceptions.RequestException as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue

    raise last_exc
