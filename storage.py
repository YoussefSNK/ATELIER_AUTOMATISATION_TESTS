"""SQLite storage for test runs."""

import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            api TEXT NOT NULL,
            passed INTEGER NOT NULL,
            failed INTEGER NOT NULL,
            error_rate REAL NOT NULL,
            latency_avg REAL NOT NULL,
            latency_p95 REAL NOT NULL,
            availability REAL NOT NULL,
            details TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_run(run_data):
    """Persist a run result dict to SQLite."""
    conn = _connect()
    s = run_data["summary"]
    conn.execute(
        """INSERT INTO runs
           (timestamp, api, passed, failed, error_rate, latency_avg, latency_p95, availability, details)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            run_data["timestamp"],
            run_data["api"],
            s["passed"],
            s["failed"],
            s["error_rate"],
            s["latency_ms_avg"],
            s["latency_ms_p95"],
            s["availability"],
            json.dumps(run_data["tests"]),
        ),
    )
    conn.commit()
    conn.close()


def list_runs(limit=50):
    """Return the most recent runs (newest first)."""
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_run(run_id):
    """Return a single run by id."""
    conn = _connect()
    row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
