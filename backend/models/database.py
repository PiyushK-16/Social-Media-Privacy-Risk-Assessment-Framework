"""
database.py - privacy-first SQLite storage.

STORED:   assessment_id, overall score, risk level, created_at, category scores,
          finding types (+ category/severity/description) and a HASH of the delete token.
NEVER STORED: raw answers, phone, e-mail, address, birth date, passwords, exact
          location, private messages, IP addresses.
"""
import hashlib
import hmac
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from services.recommendation_engine import RECOMMENDATION_CATALOG

SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id     TEXT PRIMARY KEY,
    overall_score     INTEGER NOT NULL CHECK (overall_score BETWEEN 0 AND 100),
    risk_level        TEXT NOT NULL CHECK (risk_level IN ('LOW','MODERATE','HIGH','CRITICAL')),
    created_at        TEXT NOT NULL,
    delete_token_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS category_scores (
    category_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id     TEXT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    category          TEXT NOT NULL,
    score             REAL NOT NULL CHECK (score BETWEEN 0 AND 100)
);
CREATE TABLE IF NOT EXISTS findings (
    finding_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    category      TEXT NOT NULL,
    finding_type  TEXT NOT NULL,
    severity      TEXT NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH')),
    description   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_type      TEXT NOT NULL UNIQUE,
    recommendation    TEXT NOT NULL,
    priority          TEXT NOT NULL CHECK (priority IN ('IMMEDIATE','IMPORTANT','GOOD PRACTICE'))
);
"""


@contextmanager
def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        for r in RECOMMENDATION_CATALOG:   # seed the static recommendation table
            conn.execute("INSERT OR IGNORE INTO recommendations (finding_type, recommendation, priority) VALUES (?,?,?)",
                         (r["finding_type"], r["recommendation"], r["priority"]))


def _hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def save_assessment(db_path, result):
    """Persist ONLY the minimal result. Returns (assessment_id, delete_token, created_at)."""
    assessment_id = "PRA-" + secrets.token_hex(8).upper()      # unguessable, random
    delete_token = secrets.token_urlsafe(24)
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect(db_path) as conn:
        conn.execute("INSERT INTO assessments VALUES (?,?,?,?,?)",
                     (assessment_id, result["overall_score"], result["risk_level"], created_at, _hash_token(delete_token)))
        conn.executemany("INSERT INTO category_scores (assessment_id, category, score) VALUES (?,?,?)",
                         [(assessment_id, k, v) for k, v in result["category_scores"].items()])
        conn.executemany("INSERT INTO findings (assessment_id, category, finding_type, severity, description) VALUES (?,?,?,?,?)",
                         [(assessment_id, f["category"], f["finding_type"], f["severity"], f["description"])
                          for f in result["findings"]])
    return assessment_id, delete_token, created_at


def get_assessment(db_path, assessment_id):
    with connect(db_path) as conn:
        a = conn.execute("SELECT assessment_id, overall_score, risk_level, created_at FROM assessments WHERE assessment_id=?",
                         (assessment_id,)).fetchone()
        if not a:
            return None
        cats = conn.execute("SELECT category, score FROM category_scores WHERE assessment_id=? ORDER BY category_score_id",
                            (assessment_id,)).fetchall()
        finds = conn.execute("SELECT category, finding_type, severity, description FROM findings WHERE assessment_id=? ORDER BY finding_id",
                             (assessment_id,)).fetchall()
    return {**dict(a), "category_scores": {c["category"]: c["score"] for c in cats},
            "findings": [dict(f) for f in finds]}


def get_recommendations(db_path, assessment_id):
    order = "CASE r.priority WHEN 'IMMEDIATE' THEN 3 WHEN 'IMPORTANT' THEN 2 ELSE 1 END DESC, " \
            "CASE f.severity WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 ELSE 1 END DESC, f.finding_id"
    with connect(db_path) as conn:
        if not conn.execute("SELECT 1 FROM assessments WHERE assessment_id=?", (assessment_id,)).fetchone():
            return None
        rows = conn.execute(
            f"SELECT r.finding_type, r.recommendation, r.priority FROM findings f "
            f"JOIN recommendations r ON r.finding_type=f.finding_type WHERE f.assessment_id=? ORDER BY {order}",
            (assessment_id,)).fetchall()
    return [dict(r) for r in rows]


def delete_assessment(db_path, assessment_id, token):
    """Returns 'deleted', 'forbidden' or 'not_found'. Token compared in constant time."""
    with connect(db_path) as conn:
        row = conn.execute("SELECT delete_token_hash FROM assessments WHERE assessment_id=?", (assessment_id,)).fetchone()
        if not row:
            return "not_found"
        if not token or not hmac.compare_digest(row["delete_token_hash"], _hash_token(token)):
            return "forbidden"
        conn.execute("DELETE FROM assessments WHERE assessment_id=?", (assessment_id,))
    return "deleted"


def purge_older_than(db_path, days):
    """Retention limitation: remove assessments older than N days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    with connect(db_path) as conn:
        return conn.execute("DELETE FROM assessments WHERE created_at < ?", (cutoff,)).rowcount


def live_stats(db_path):
    with connect(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) c FROM assessments").fetchone()["c"]
        levels = {r["risk_level"]: r["c"] for r in conn.execute(
            "SELECT risk_level, COUNT(*) c FROM assessments GROUP BY risk_level")}
        avg = conn.execute("SELECT AVG(overall_score) a FROM assessments").fetchone()["a"]
    return {"total_assessments": total, "level_counts": levels, "average_score": round(avg, 1) if avg is not None else None}
