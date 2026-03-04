import json
from flask import Flask, render_template, jsonify, request

from tester.runner import run_all
from storage import save_run, list_runs, get_run

app = Flask(__name__)

# Anti-spam: minimum seconds between runs
import time
_last_run_ts = 0
MIN_RUN_INTERVAL = 30


@app.get("/")
def index():
    return render_template("dashboard.html", runs=list_runs(20), active="dashboard")


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html", runs=list_runs(20), active="dashboard")


@app.post("/run")
def trigger_run():
    global _last_run_ts
    now = time.time()
    if now - _last_run_ts < MIN_RUN_INTERVAL:
        wait = int(MIN_RUN_INTERVAL - (now - _last_run_ts))
        return jsonify({"error": f"Rate limited. Wait {wait}s."}), 429

    _last_run_ts = now
    result = run_all()
    save_run(result)
    return jsonify(result), 201


@app.get("/run/<int:run_id>")
def view_run(run_id):
    r = get_run(run_id)
    if not r:
        return jsonify({"error": "Run not found"}), 404
    r["tests"] = json.loads(r["details"])
    return render_template("run_detail.html", run=r, active="dashboard")


@app.get("/api/runs")
def api_runs():
    """JSON export of all runs."""
    runs = list_runs(100)
    for r in runs:
        r["tests"] = json.loads(r["details"])
        del r["details"]
    return jsonify(runs)


@app.get("/api/runs/<int:run_id>")
def api_run_detail(run_id):
    r = get_run(run_id)
    if not r:
        return jsonify({"error": "Run not found"}), 404
    r["tests"] = json.loads(r["details"])
    del r["details"]
    return jsonify(r)


@app.get("/health")
def health():
    runs = list_runs(1)
    if not runs:
        return jsonify({"status": "no_data", "message": "No runs yet"}), 200
    last = runs[0]
    status = "healthy" if last["failed"] == 0 else "degraded"
    return jsonify({
        "status": status,
        "last_run": last["timestamp"],
        "passed": last["passed"],
        "failed": last["failed"],
        "availability": last["availability"],
        "latency_avg_ms": last["latency_avg"],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
